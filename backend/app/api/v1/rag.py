"""API RAG Rulebook — preview chunk, ingest embedding, tìm kiếm."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.deps import get_db
from app.repositories.rulebook_rag_repository import RulebookRagRepository
from app.schemas.rag import (
    RulebookChunkPreviewResponse,
    RulebookIngestResponse,
    RulebookRagStatsResponse,
    RulebookSearchRequest,
    RulebookSearchResponse,
)
from app.services.rulebook_rag_service import RulebookRagService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/rag/rulebook", tags=["rag-rulebook"])
_service = RulebookRagService()


@router.post("/preview", response_model=RulebookChunkPreviewResponse)
async def preview_rulebook_chunks(
    file: UploadFile = File(...),
) -> RulebookChunkPreviewResponse:
    """Upload file .md và xem trước các chunk theo ## (chưa embed)."""
    try:
        filename, text = await _service.read_upload(file)
        return _service.preview(filename, text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ingest", response_model=RulebookIngestResponse)
async def ingest_rulebook_chunks(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> RulebookIngestResponse:
    """
    Upload Rulebook, cắt chunk, gọi LM Studio embedding và lưu pgvector.

    Yêu cầu LM Studio đang chạy với model text-embedding-embeddinggamma-300m-qat.
    """
    try:
        filename, text = await _service.read_upload(file)
        repo = RulebookRagRepository(session)
        return await _service.ingest(repo, filename, text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/stats", response_model=RulebookRagStatsResponse)
async def rulebook_rag_stats(
    session: AsyncSession = Depends(get_db),
) -> RulebookRagStatsResponse:
    """Thống kê chunk đã lưu trong database RAG."""
    repo = RulebookRagRepository(session)
    return await _service.get_stats(repo)


@router.post("/search", response_model=RulebookSearchResponse)
async def search_rulebook_rag(
    body: RulebookSearchRequest,
    session: AsyncSession = Depends(get_db),
) -> RulebookSearchResponse:
    """Semantic search trên các chunk Rulebook đã ingest."""
    repo = RulebookRagRepository(session)
    try:
        return await _service.search(
            repo,
            body.query,
            limit=body.limit,
            rag_scope=body.rag_scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
