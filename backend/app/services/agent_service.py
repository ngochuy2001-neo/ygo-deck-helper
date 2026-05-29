"""Service chạy AgentScope DeckHelper agent từ backend."""

from __future__ import annotations

import sys
from pathlib import Path

from app.services.lm_studio_service import load_lm_studio_settings

AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from agentscope.message import UserMsg  # noqa: E402

from config.lm_studio import LMStudioConfig  # noqa: E402
from workflows.react_deck_agent import (  # noqa: E402
    create_deck_helper_agent,
    extract_text_from_msg,
)


def _to_agent_config() -> LMStudioConfig:
    settings = load_lm_studio_settings()
    return LMStudioConfig.model_validate(settings.model_dump())


async def run_deck_helper_chat(message: str) -> tuple[str, str]:
    """
    Chạy một lượt chat với DeckHelper agent.

    Returns:
        Tuple (reply_text, model_name).

    Raises:
        ValueError: Khi chưa cấu hình model.
    """
    config = _to_agent_config()
    if not config.model_name.strip():
        raise ValueError("Chưa chọn model LM Studio. Vui lòng cấu hình trong Settings.")

    agent = create_deck_helper_agent(config, max_iters=10, stream=False)
    reply = await agent.reply(UserMsg(name="user", content=message))
    return extract_text_from_msg(reply), config.model_name
