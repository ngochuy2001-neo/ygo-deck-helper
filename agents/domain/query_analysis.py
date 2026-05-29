"""Mô hình và parser kết quả phân tích câu hỏi trước khi gọi agent trả lời."""

from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    """Ý định chính của người dùng."""

    RULE_QUESTION = "rule_question"
    DECK_BUILD = "deck_build"
    CARD_LOOKUP = "card_lookup"
    COMBO = "combo"
    GENERAL = "general"
    UNCLEAR = "unclear"


class QueryAnalysis(BaseModel):
    """Kết quả chuẩn hóa từ QueryAnalyzer agent."""

    intent: QueryIntent = QueryIntent.GENERAL
    rag_scope: str = ""
    language: str = "vi"
    entities: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    clarified_question: str = ""
    rag_search_queries: list[str] = Field(default_factory=list)
    answer_focus: str = ""
    do_not_assume: list[str] = Field(default_factory=list)


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)
_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")


def _coerce_intent(value: Any) -> QueryIntent:
    if isinstance(value, QueryIntent):
        return value
    raw = str(value or "").strip().lower()
    try:
        return QueryIntent(raw)
    except ValueError:
        return QueryIntent.UNCLEAR


def _coerce_str_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def parse_query_analysis(raw_text: str, *, fallback_question: str = "") -> QueryAnalysis:
    """
    Trích JSON từ output LLM; fallback an toàn khi parse thất bại.
    """
    text = (raw_text or "").strip()
    candidates: list[str] = []

    for match in _JSON_FENCE_RE.finditer(text):
        candidates.append(match.group(1))

    if not candidates:
        obj_match = _JSON_OBJECT_RE.search(text)
        if obj_match:
            candidates.append(obj_match.group(0))

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        return QueryAnalysis(
            intent=_coerce_intent(data.get("intent")),
            rag_scope=str(data.get("rag_scope") or "").strip(),
            language=str(data.get("language") or "vi").strip() or "vi",
            entities=_coerce_str_list(data.get("entities")),
            ambiguities=_coerce_str_list(data.get("ambiguities")),
            clarified_question=str(
                data.get("clarified_question") or fallback_question
            ).strip()
            or fallback_question,
            rag_search_queries=_coerce_str_list(data.get("rag_search_queries")),
            answer_focus=str(data.get("answer_focus") or "").strip(),
            do_not_assume=_coerce_str_list(data.get("do_not_assume")),
        )

    question = fallback_question.strip()
    return QueryAnalysis(
        intent=QueryIntent.UNCLEAR,
        clarified_question=question,
        rag_search_queries=[question] if question else [],
        answer_focus="Trả lời đúng câu hỏi gốc; không suy diễn thêm.",
        ambiguities=["Không phân tích được JSON từ QueryAnalyzer — dùng câu hỏi gốc."],
    )


def rag_queries_for_search(analysis: QueryAnalysis, original: str) -> list[str]:
    """Danh sách truy vấn RAG (dedupe, giữ thứ tự)."""
    seen: set[str] = set()
    ordered: list[str] = []

    for candidate in [*analysis.rag_search_queries, analysis.clarified_question, original]:
        q = candidate.strip()
        if not q:
            continue
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(q)

    return ordered[:4]


def format_rulebook_agent_input(
    original: str,
    analysis: QueryAnalysis,
    *,
    rag_context: str = "",
) -> str:
    """Gắn brief phân tích + RAG cho Rulebook Lab agent."""
    lines = [
        f"Câu hỏi gốc (người chơi): {original}",
        f"Câu hỏi đã chuẩn hóa: {analysis.clarified_question}",
        f"Ý định: {analysis.intent.value}",
        f"Trọng tâm trả lời: {analysis.answer_focus or '(theo câu hỏi chuẩn hóa)'}",
    ]
    if analysis.entities:
        lines.append(f"Thực thể / thuật ngữ: {', '.join(analysis.entities)}")
    if analysis.ambiguities:
        lines.append(f"Điểm mơ hồ (trả lời cẩn thận): {'; '.join(analysis.ambiguities)}")
    if analysis.do_not_assume:
        lines.append(f"Không được giả định: {'; '.join(analysis.do_not_assume)}")

    header = "\n".join(lines)
    if not rag_context.strip():
        return (
            f"{header}\n\n---\n"
            "Hãy giải thích bằng tiếng Việt. Gọi tool chỉ khi thiếu thông tin trong Rulebook."
        )

    return (
        f"{header}\n\n---\n"
        "Đoạn Rulebook chính thức (RAG — nguồn trả lời):\n"
        f"{rag_context}\n"
        "---\n"
        "Hãy giải thích bằng tiếng Việt, dựa trên các đoạn trên. "
        "Chỉ gọi tool nếu thiếu thông tin."
    )


def format_deck_helper_input(original: str, analysis: QueryAnalysis) -> str:
    """Gắn brief phân tích cho DeckHelper agent."""
    lines = [
        f"Yêu cầu gốc: {original}",
        f"Yêu cầu đã chuẩn hóa: {analysis.clarified_question}",
        f"Loại yêu cầu: {analysis.intent.value}",
        f"Hướng trả lời: {analysis.answer_focus or '(theo yêu cầu chuẩn hóa)'}",
    ]
    if analysis.entities:
        lines.append(f"Lá bài / archetype / format liên quan: {', '.join(analysis.entities)}")
    if analysis.do_not_assume:
        lines.append(f"Không giả định: {'; '.join(analysis.do_not_assume)}")

    return (
        "\n".join(lines)
        + "\n\n---\nTrả lời người chơi theo yêu cầu đã chuẩn hóa. "
        "Dùng tool khi cần dữ liệu thật."
    )
