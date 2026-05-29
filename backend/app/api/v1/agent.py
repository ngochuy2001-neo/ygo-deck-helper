"""API kích hoạt và theo dõi Agent."""

from fastapi import APIRouter, HTTPException

from app.schemas.lm_studio import AgentChatRequest, AgentChatResponse
from app.services.agent_service import run_deck_helper_chat

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(payload: AgentChatRequest) -> AgentChatResponse:
    """
    Gửi tin nhắn tới DeckHelper ReAct agent (AgentScope + LM Studio).

    Yêu cầu LM Studio đang chạy và model đã được chọn trong Settings.
    """
    try:
        reply, model_name = await run_deck_helper_chat(payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — trả lỗi chi tiết cho client
        raise HTTPException(
            status_code=502,
            detail=f"Agent thất bại: {exc}",
        ) from exc

    return AgentChatResponse(reply=reply, model_name=model_name)
