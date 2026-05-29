"""
ReAct Agent hỗ trợ xây dựng deck Yu-Gi-Oh! (DeckHelper).

Sử dụng AgentScope 2.x với LM Studio làm model provider (OpenAI-compatible).
"""

from __future__ import annotations

from typing import Any

from agentscope.agent import Agent, ReActConfig
from agentscope.message import Msg, TextBlock
from agentscope.tool import Toolkit

from config.lm_studio import LMStudioConfig, create_openai_chat_model, load_config
from tools.allowed_function_tool import AllowedFunctionTool
from tools.db_queries import query_card_database
from tools.web_search import web_search

DECK_HELPER_SYSTEM_PROMPT = """\
Bạn là DeckHelper — trợ lý AI chuyên xây dựng deck Yu-Gi-Oh! (YGO).

Nhiệm vụ:
- Gợi ý lá bài, combo, và cấu trúc deck theo archetype hoặc mục tiêu người chơi.
- Tra cứu thông tin qua tools khi cần (web_search, db_queries).
- Trả lời ngắn gọn, rõ ràng, ưu tiên tiếng Việt nếu người dùng dùng tiếng Việt.

Khi chưa có dữ liệu thật từ tool, hãy nói rõ và đưa gợi ý chung dựa trên kiến thức sẵn có.\
"""


def _build_toolkit() -> Toolkit:
    return Toolkit(
        tools=[
            AllowedFunctionTool(web_search),
            AllowedFunctionTool(query_card_database),
        ],
    )


def create_deck_helper_agent(
    config: LMStudioConfig | None = None,
    *,
    max_iters: int = 10,
    stream: bool = False,
    **model_kwargs: Any,
) -> Agent:
    """
    Tạo và trả về instance DeckHelper ReAct agent.

    Args:
        config: Cấu hình LM Studio; mặc định đọc từ agents/config/lm_studio.json.
        max_iters: Số vòng ReAct tối đa (guardrail chống vòng lặp vô hạn).
        stream: Bật streaming response từ model.
        **model_kwargs: Tham số bổ sung cho OpenAIChatModel.Parameters (temperature, ...).

    Returns:
        AgentScope Agent instance.
    """
    cfg = config or load_config()
    model = create_openai_chat_model(cfg, stream=stream, **model_kwargs)

    return Agent(
        name="DeckHelper",
        system_prompt=DECK_HELPER_SYSTEM_PROMPT,
        model=model,
        toolkit=_build_toolkit(),
        react_config=ReActConfig(max_iters=max_iters),
    )


def extract_text_from_msg(msg: Msg) -> str:
    """Trích xuất nội dung text từ Msg trả về của agent."""
    if isinstance(msg.content, str):
        return msg.content

    parts: list[str] = []
    for block in msg.content:
        if isinstance(block, TextBlock):
            parts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))

    return "\n".join(part for part in parts if part).strip()
