"""Pydantic schemas cho API cards (sync, stats)."""

from datetime import datetime

from pydantic import BaseModel, Field


class CardSyncRequest(BaseModel):
    force: bool = False


class CardSyncJobResponse(BaseModel):
    id: int
    status: str
    force: bool
    api_db_version_before: str | None = None
    api_db_version_after: str | None = None
    total_expected: int | None = None
    total_fetched: int
    inserted: int
    updated: int
    images_downloaded: int
    errors_count: int
    error_message: str | None = None
    started_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class CardStatsResponse(BaseModel):
    total_cards: int
    last_sync_at: datetime | None = None
    api_db_version: str | None = None
    sync_in_progress: bool = False
