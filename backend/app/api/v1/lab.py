"""API tab thử nghiệm — AgentScope + Rulebook RAG + Gemma."""

from fastapi import APIRouter, HTTPException

from app.schemas.lab import LabChatRequest, LabChatResponse, LabInfoResponse
from app.services.lab_agent_service import get_lab_info, run_lab_chat

router = APIRouter(prefix="/lab", tags=["lab"])


@router.get("/info", response_model=LabInfoResponse)
async def lab_info() -> LabInfoResponse:
    """Trạng thái kết nối LM Studio, RAG và model lab."""
    return await get_lab_info()


@router.post("/chat", response_model=LabChatResponse)
async def lab_chat(payload: LabChatRequest) -> LabChatResponse:
    """
    Chat thử nghiệm với AgentScope Rulebook Lab.

    Model chat mặc định: google/gemma-4-e4b (LAB_CHAT_MODEL).
    RAG: text-embedding-embeddinggamma-300m-qat + pgvector.
    """
    try:
        return await run_lab_chat(
            payload.message,
            use_rag=payload.use_rag,
            use_query_analyzer=payload.use_query_analyzer,
            rag_limit=payload.rag_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Lab agent thất bại: {exc}",
        ) from exc
