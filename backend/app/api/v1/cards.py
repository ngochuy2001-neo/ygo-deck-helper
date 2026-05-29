"""API đồng bộ, thống kê và tra cứu lá bài YGO."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps.card_search import card_search_params
from app.core.database import AsyncSessionLocal
from app.repositories.card_repository import CardRepository
from app.schemas.card_catalog import CardDetailResponse, CardListResponse
from app.schemas.card_search import CardFilterOptionsResponse, CardSearchParams
from app.schemas.cards import (
    CardStatsResponse,
    CardSyncJobResponse,
    CardSyncRequest,
)
from app.services.card_catalog_service import CardCatalogService
from app.services.card_sync_service import CardSyncService

router = APIRouter(prefix="/cards", tags=["cards"])
_sync_service = CardSyncService()


@router.get("", response_model=CardListResponse)
async def list_cards(
    params: CardSearchParams = Depends(card_search_params),
) -> CardListResponse:
    """Danh sách lá bài (phân trang, tìm kiếm và bộ lọc YGO)."""
    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        service = CardCatalogService(repo)
        return await service.search_cards(params)


@router.get("/filter-options", response_model=CardFilterOptionsResponse)
async def get_card_filter_options() -> CardFilterOptionsResponse:
    """Metadata giá trị distinct cho UI bộ lọc."""
    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        service = CardCatalogService(repo)
        return await service.get_filter_options()


@router.post("/sync", response_model=CardSyncJobResponse)
async def start_card_sync(body: CardSyncRequest) -> CardSyncJobResponse:
    """Khởi chạy đồng bộ lá bài từ YGOPRODeck (chạy nền)."""
    try:
        job_id = await _sync_service.start_sync(force=body.force)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        job = await repo.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=500, detail="Không tạo được sync job.")
        return CardSyncJobResponse.model_validate(job)


@router.get("/sync/latest", response_model=CardSyncJobResponse | None)
async def get_latest_sync_job() -> CardSyncJobResponse | None:
    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        job = await repo.get_latest_job()
        if job is None:
            return None
        return CardSyncJobResponse.model_validate(job)


@router.get("/sync/{job_id}", response_model=CardSyncJobResponse)
async def get_sync_job(job_id: int) -> CardSyncJobResponse:
    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        job = await repo.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Sync job không tồn tại.")
        return CardSyncJobResponse.model_validate(job)


@router.get("/stats", response_model=CardStatsResponse)
async def get_card_stats() -> CardStatsResponse:
    stats = await _sync_service.get_stats()
    return CardStatsResponse(**stats)


@router.get("/{passcode}", response_model=CardDetailResponse)
async def get_card_detail(passcode: int) -> CardDetailResponse:
    """Chi tiết một lá bài theo passcode."""
    async with AsyncSessionLocal() as session:
        repo = CardRepository(session)
        service = CardCatalogService(repo)
        card = await service.get_card(passcode)
        if card is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy lá bài.")
        return card
