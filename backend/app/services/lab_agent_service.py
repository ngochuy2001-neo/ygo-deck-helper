"""AgentScope lab: Gemma + Rulebook RAG."""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.repositories.rulebook_rag_repository import RulebookRagRepository
from app.schemas.lab import LabChatResponse, LabInfoResponse, LabRagHitBrief
from app.schemas.rag import RulebookSearchHit
from app.services.embedding_service import EmbeddingServiceError
from app.services.lm_studio_service import check_lm_studio_status, load_lm_studio_settings
from app.services.query_analyzer_service import analysis_to_brief, run_query_analysis
from app.services.rulebook_rag_service import RulebookRagService

AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from config.lm_studio import LMStudioConfig  # noqa: E402
from domain.query_analysis import rag_queries_for_search  # noqa: E402
from domain.rag_context_builder import (  # noqa: E402
    build_structured_rag_context,
    format_judge_lab_user_payload,
)
from domain.rule_rag_intent import (  # noqa: E402
    classify_rule_rag_intent,
    rag_search_queries_for_intent,
)
from workflows.agent_runner import run_agent_until_answer  # noqa: E402
from workflows.query_analyzer_agent import AnalyzerDomain  # noqa: E402
from workflows.rulebook_lab_agent import (  # noqa: E402
    create_rulebook_lab_agent,
    extract_text_from_msg,
)

_rag_service = RulebookRagService()


def _lab_chat_model() -> str:
    return settings.LAB_CHAT_MODEL.strip() or "google/gemma-4-e4b"


def _to_lab_agent_config() -> LMStudioConfig:
    lm = load_lm_studio_settings()
    base = LMStudioConfig.model_validate(lm.model_dump())
    return base.model_copy(update={"model_name": _lab_chat_model()})


def _hits_to_brief(hits: list[RulebookSearchHit]) -> list[LabRagHitBrief]:
    briefs: list[LabRagHitBrief] = []
    for hit in hits:
        excerpt = hit.content[:800] + ("…" if len(hit.content) > 800 else "")
        briefs.append(
            LabRagHitBrief(
                chunk_id=hit.chunk_id,
                title=hit.title,
                description=hit.description,
                distance=hit.distance,
                excerpt=excerpt,
            )
        )
    return briefs


async def _prefetch_rag_queries(
    queries: list[str],
    limit: int,
    *,
    rag_scope: str,
    clarified_question: str,
) -> list[RulebookSearchHit]:
    """Retrieve RAG có lọc intent; merge theo chunk_id."""
    if not queries:
        return []

    merged: dict[str, RulebookSearchHit] = {}
    async with AsyncSessionLocal() as session:
        repo = RulebookRagRepository(session)
        stats = await repo.get_stats()
        if not stats.get("total_chunks"):
            return []

        for query in queries:
            try:
                result = await _rag_service.search(
                    repo,
                    query,
                    limit=limit,
                    rag_scope=rag_scope,
                    clarified_question=clarified_question,
                )
            except (ValueError, EmbeddingServiceError):
                continue
            for hit in result.hits:
                existing = merged.get(hit.chunk_id)
                if existing is None or hit.distance < existing.distance:
                    merged[hit.chunk_id] = hit

    return sorted(merged.values(), key=lambda hit: hit.distance)[:limit]


async def run_lab_chat(
    message: str,
    *,
    use_rag: bool = True,
    use_query_analyzer: bool = True,
    rag_limit: int = 3,
) -> LabChatResponse:
    """
    Luồng: QueryAnalyzer → phân loại RAG intent → RAG lọc nguồn → Judge Lab agent.
    """
    config = _to_lab_agent_config()
    if not config.model_name.strip():
        raise ValueError("Chưa cấu hình model chat cho lab.")

    analysis = await run_query_analysis(
        message,
        config,
        domain=AnalyzerDomain.RULEBOOK,
        enabled=use_query_analyzer,
    )
    analysis_brief = analysis_to_brief(analysis)

    rag_intent = classify_rule_rag_intent(
        message,
        rag_scope=analysis.rag_scope,
        clarified_question=analysis.clarified_question,
    )
    if use_query_analyzer and not analysis.rag_scope:
        analysis_brief = analysis_brief.model_copy(
            update={"rag_scope": rag_intent.value}
        )

    rag_hits_raw: list[RulebookSearchHit] = []
    search_queries: list[str] = []
    if use_rag:
        base_queries = rag_queries_for_search(analysis, message)
        search_queries = rag_search_queries_for_intent(
            rag_intent, base_queries, message
        )
        rag_hits_raw = await _prefetch_rag_queries(
            search_queries,
            rag_limit,
            rag_scope=rag_intent.value,
            clarified_question=analysis.clarified_question or message,
        )

    structured = build_structured_rag_context(
        rag_hits_raw if use_rag else [],
        rag_intent,
    )
    analysis_dict = analysis_brief.model_dump() if use_query_analyzer else None
    user_content = format_judge_lab_user_payload(
        user_query=analysis.clarified_question or message,
        rag_context=structured,
        analysis_brief=analysis_dict,
    )

    agent = create_rulebook_lab_agent(config, max_iters=8, stream=False)
    reply = await run_agent_until_answer(agent, user_content)
    reply_text = extract_text_from_msg(reply)

    rag_briefs = _hits_to_brief(rag_hits_raw)
    if _is_waiting_placeholder(reply_text) and rag_briefs:
        reply_text = _synthesize_from_rag(analysis.clarified_question or message, rag_briefs)

    return LabChatResponse(
        reply=reply_text,
        model_name=config.model_name,
        embedding_model=settings.RAG_EMBEDDING_MODEL,
        rag_used=use_rag and len(rag_briefs) > 0,
        rag_hits=rag_briefs,
        query_analysis=analysis_brief if use_query_analyzer else None,
        rag_scope=rag_intent.value,
    )


def _is_waiting_placeholder(text: str) -> bool:
    markers = (
        "waiting for tool calls",
        "executed maximum iterations",
    )
    lowered = text.strip().lower()
    return not lowered or any(marker in lowered for marker in markers)


def _summarize_principle(excerpt: str, *, max_len: int = 180) -> str:
    """Rút gọn excerpt thành 1–2 câu nguyên tắc, không dump block dài."""
    text = " ".join(excerpt.split())
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return cut + "…"


def _synthesize_from_rag(question: str, rag_hits: list[LabRagHitBrief]) -> str:
    """Fallback khi ReAct dừng sớm: tóm tắt nguyên tắc từ chunk RAG đã có."""
    lines = [
        "*(Agent chưa tổng hợp xong — dưới đây là nguyên tắc liên quan từ Rulebook)*\n",
        "**Kết luận:** Chưa đủ context để ruling chắc chắn cho câu hỏi này.\n",
        f"**Câu hỏi:** {question}\n",
        "**Nguyên tắc áp dụng được:**",
    ]
    for hit in rag_hits:
        principle = _summarize_principle(hit.excerpt)
        lines.append(f"\n- **{hit.title}** [`{hit.chunk_id}`]: {principle}")
    lines.append(
        "\n\n*Hãy hỏi lại cụ thể hơn (loại bài, timing, ai phản ứng trước). "
        "Nếu vẫn lỗi, restart backend sau khi cập nhật code.*"
    )
    return "\n".join(lines)


async def get_lab_info() -> LabInfoResponse:
    """Trạng thái lab: model, RAG, LM Studio."""
    status = await check_lm_studio_status()
    async with AsyncSessionLocal() as session:
        repo = RulebookRagRepository(session)
        stats = await repo.get_stats()

    total = int(stats.get("total_chunks") or 0)
    rag_ready = total > 0
    chat_model = _lab_chat_model()
    sources = stats.get("source_filenames") or []

    if not status.connected:
        msg = "LM Studio chưa kết nối — bật server và load model Gemma."
    elif not rag_ready:
        msg = "RAG chưa có chunk — ingest Rulebook tại trang Rulebook RAG."
    else:
        msg = (
            f"Sẵn sàng: {chat_model} + Rulebook RAG ({total} chunk). "
            "Intent RAG: chain vs conjunction đã bật."
        )
        if sources:
            msg += f" Nguồn: {', '.join(str(s) for s in sources[:4])}."

    return LabInfoResponse(
        chat_model=chat_model,
        embedding_model=settings.RAG_EMBEDDING_MODEL,
        rag_chunks_in_db=total,
        rag_ready=rag_ready,
        lm_studio_connected=status.connected,
        message=msg,
    )
