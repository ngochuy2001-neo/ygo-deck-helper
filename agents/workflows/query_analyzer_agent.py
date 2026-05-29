"""
QueryAnalyzer — agent phân tích câu hỏi trước khi agent trả lời chính.

Không dùng tool; output JSON để backend parse và inject context.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from agentscope.agent import Agent, ReActConfig

from config.lm_studio import LMStudioConfig, create_openai_chat_model, load_config
from domain.query_analysis import QueryAnalysis, parse_query_analysis
from workflows.agent_runner import run_agent_until_answer
from workflows.react_deck_agent import extract_text_from_msg


class AnalyzerDomain(str, Enum):
    """Ngữ cảnh agent đích sẽ nhận câu hỏi."""

    RULEBOOK = "rulebook"
    DECK = "deck"


_QUERY_ANALYZER_BASE_PROMPT = """\
Bạn là QueryAnalyzer — chuyên gia phân tích câu hỏi Yu-Gi-Oh! TRƯỚC KHI agent khác trả lời.

Bạn KHÔNG trả lời câu hỏi gốc. Chỉ phân tích, làm rõ và chuẩn hóa.

Output: CHỈ một object JSON hợp lệ (không markdown, không text thừa) với các field:
- intent: rule_question | deck_build | card_lookup | combo | general | unclear
- rag_scope: chain_interaction | card_text_resolution | general_rulebook
  (chain = tranh chấp Chain/destroy/negate; card_text = Then/Also/PSCT nội tại lá; KHÔNG nhầm hai loại)
- language: "vi" hoặc "en"
- entities: mảng string (tên lá, archetype, thuật ngữ PSCT, Timing, Zone...)
- ambiguities: mảng string — chỗ mơ hồ cần agent trả lời thận trọng
- clarified_question: câu hỏi đã làm rõ, đủ ngữ cảnh, 1–3 câu
- rag_search_queries: 1–4 cụm ngắn để semantic search Rulebook (ưu tiên thuật ngữ PSCT tiếng Anh)
- answer_focus: 1–2 câu hướng dẫn agent trả lời đúng trọng tâm
- do_not_assume: điều KHÔNG được đoán nếu người dùng chưa nói

Quy tắc:
- Giữ ý người dùng; không thêm giả định về deck list, format, hoặc ruling chưa hỏi.
- Câu hỏi luật: tách timing, cost, target, chain nếu liên quan.
- Nếu câu hỏi quá mơ hồ: intent = unclear, ghi rõ trong ambiguities.\
"""

_DOMAIN_SUFFIX: dict[AnalyzerDomain, str] = {
    AnalyzerDomain.RULEBOOK: (
        "\n\nNgữ cảnh: câu hỏi sẽ gửi tới agent giải thích Rulebook / PSCT. "
        "rag_scope BẮT BUỘC chính xác: destroy trên Chain → chain_interaction; "
        "Then/Also/dấu : ; trên 1 lá → card_text_resolution. "
        "rag_search_queries dùng thuật ngữ PSCT tiếng Anh, KHÔNG dùng 'conjunction' nếu rag_scope là chain_interaction. "
        "answer_focus phải mô tả CÁCH SUY LUẬN (timing, loại bài, exception), không chỉ chủ đề — "
        "vd. 'So sánh Spell Speed và xét loại Spell (Normal vs Continuous)' thay vì 'Câu hỏi về Chain'."
    ),
    AnalyzerDomain.DECK: (
        "\n\nNgữ cảnh: câu hỏi sẽ gửi tới agent xây deck. "
        "rag_search_queries có thể rỗng []. "
        "Ưu tiên intent deck_build / combo / card_lookup khi phù hợp."
    ),
}


def _system_prompt(domain: AnalyzerDomain) -> str:
    return _QUERY_ANALYZER_BASE_PROMPT + _DOMAIN_SUFFIX[domain]


def create_query_analyzer_agent(
    config: LMStudioConfig | None = None,
    *,
    domain: AnalyzerDomain = AnalyzerDomain.RULEBOOK,
    stream: bool = False,
    **model_kwargs: Any,
) -> Agent:
    """
    Agent không tool — một lượt sinh JSON phân tích.
    """
    cfg = config or load_config()
    model = create_openai_chat_model(cfg, stream=stream, **model_kwargs)

    return Agent(
        name="QueryAnalyzer",
        system_prompt=_system_prompt(domain),
        model=model,
        react_config=ReActConfig(max_iters=1),
    )


async def analyze_user_query(
    user_message: str,
    config: LMStudioConfig,
    *,
    domain: AnalyzerDomain = AnalyzerDomain.RULEBOOK,
) -> QueryAnalysis:
    """
    Chạy QueryAnalyzer và parse JSON.

    Khi LLM lỗi format, trả về fallback an toàn từ câu hỏi gốc.
    """
    question = user_message.strip()
    if not question:
        return QueryAnalysis(clarified_question="")

    agent = create_query_analyzer_agent(config, domain=domain)
    prompt = (
        f"Phân tích câu hỏi sau (domain={domain.value}):\n\n{question}"
    )
    reply = await run_agent_until_answer(agent, prompt, max_continuations=1)
    raw = extract_text_from_msg(reply)
    return parse_query_analysis(raw, fallback_question=question)
