"""Service chạy AgentScope DeckHelper agent từ backend."""

from __future__ import annotations

import sys
from pathlib import Path

from app.services.lm_studio_service import load_lm_studio_settings
from app.services.query_analyzer_service import run_query_analysis

AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from config.lm_studio import LMStudioConfig  # noqa: E402
from domain.query_analysis import format_deck_helper_input  # noqa: E402
from workflows.agent_runner import run_agent_until_answer  # noqa: E402
from workflows.query_analyzer_agent import AnalyzerDomain  # noqa: E402
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

    analysis = await run_query_analysis(
        message,
        config,
        domain=AnalyzerDomain.DECK,
    )
    agent_input = format_deck_helper_input(message, analysis)

    agent = create_deck_helper_agent(config, max_iters=10, stream=False)
    reply = await run_agent_until_answer(agent, agent_input)
    return extract_text_from_msg(reply), config.model_name
