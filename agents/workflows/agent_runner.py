"""Chạy AgentScope agent tới khi có câu trả lời hoàn chỉnh (tự confirm tool)."""

from __future__ import annotations

from agentscope.agent import Agent
from agentscope.event import ConfirmResult, UserConfirmResultEvent
from agentscope.message import UserMsg

from workflows.react_deck_agent import extract_text_from_msg

_WAITING_MARKERS = (
    "waiting for tool calls to be confirmed",
    "executed maximum iterations",
)


def _is_incomplete_reply(text: str) -> bool:
    lowered = text.strip().lower()
    if not lowered:
        return True
    return any(marker in lowered for marker in _WAITING_MARKERS)


def _pending_tool_calls(agent: Agent) -> list:
    if not agent.state.context:
        return []
    last_msg = agent.state.context[-1]
    return list(last_msg.get_content_blocks("tool_call"))


def _to_agent_input(user_message: str | object) -> object:
    """
    Chuẩn hóa input cho agent.reply.

    UserMsg trong AgentScope 2 là factory function, không dùng isinstance(..., UserMsg).
    """
    if isinstance(user_message, str):
        return UserMsg(name="user", content=user_message)
    return user_message


async def run_agent_until_answer(
    agent: Agent,
    user_message: str | object,
    *,
    max_continuations: int = 6,
) -> object:
    """
    Gọi agent.reply lặp cho tới khi có text trả lời thực sự.

    Tự động confirm tool khi AgentScope trả về trạng thái chờ xác nhận.
    """
    current = _to_agent_input(user_message)
    last_reply: object | None = None

    for _ in range(max_continuations + 1):
        last_reply = await agent.reply(current)
        text = extract_text_from_msg(last_reply)

        if not _is_incomplete_reply(text):
            return last_reply

        tool_calls = _pending_tool_calls(agent)
        if tool_calls:
            current = UserConfirmResultEvent(
                reply_id=agent.state.reply_id,
                confirm_results=[
                    ConfirmResult(confirmed=True, tool_call=tool_call)
                    for tool_call in tool_calls
                ],
            )
            continue

        current = None

    if last_reply is None:
        raise RuntimeError("Agent không tạo được tin nhắn trả lời.")

    return last_reply
