"""Đồng bộ lá bài từ YGOPRODeck API vào PostgreSQL + tải ảnh local."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.card import SyncJobStatus
from app.repositories.card_repository import CardRepository
from app.schemas.ygoprodeck import YgoCardApiSchema
from app.services.ygoprodeck_client import YgoProDeckClient

logger = logging.getLogger(__name__)

_sync_lock = asyncio.Lock()
_active_job_id: int | None = None


def _version_str(version: str | int | float) -> str:
    return str(version)


class CardSyncService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = AsyncSessionLocal,
    ) -> None:
        self._session_factory = session_factory
        self._client = YgoProDeckClient()
        self._images_root = settings.card_images_dir

    async def start_sync(self, *, force: bool) -> int:
        """Tạo job và chạy sync trong background. Trả về job_id."""
        global _active_job_id

        async with _sync_lock:
            async with self._session_factory() as session:
                repo = CardRepository(session)
                if await repo.has_processing_job():
                    raise ValueError("Đang có job đồng bộ khác đang chạy.")
                job = await repo.create_sync_job(force=force)
                await session.commit()
                job_id = job.id

            _active_job_id = job_id
            asyncio.create_task(self._run_sync(job_id, force=force))
            return job_id

    async def _run_sync(self, job_id: int, *, force: bool) -> None:
        global _active_job_id
        try:
            await self._execute_sync(job_id, force=force)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Card sync failed job_id=%s", job_id)
            async with self._session_factory() as session:
                repo = CardRepository(session)
                job = await repo.get_job(job_id)
                if job:
                    await repo.update_job(
                        job,
                        status=SyncJobStatus.FAILED.value,
                        error_message=str(exc)[:2000],
                        finished_at=datetime.now(timezone.utc),
                    )
                    await session.commit()
        finally:
            if _active_job_id == job_id:
                _active_job_id = None

    async def _execute_sync(self, job_id: int, *, force: bool) -> None:
        db_version_resp = await self._client.get_db_version()
        api_version = _version_str(db_version_resp.database_version)

        async with self._session_factory() as session:
            repo = CardRepository(session)
            job = await repo.get_job(job_id)
            if job is None:
                return

            await repo.update_job(
                job,
                api_db_version_before=api_version,
            )

            if not force:
                last = await repo.get_latest_completed_job()
                if (
                    last
                    and last.api_db_version_after == api_version
                    and last.status == SyncJobStatus.COMPLETED.value
                ):
                    await repo.update_job(
                        job,
                        status=SyncJobStatus.SKIPPED.value,
                        api_db_version_after=api_version,
                        error_message="API database version không đổi — bỏ qua sync.",
                        finished_at=datetime.now(timezone.utc),
                    )
                    await session.commit()
                    return

            await session.commit()

        page_size = settings.CARD_SYNC_PAGE_SIZE
        offset = 0
        total_expected: int | None = None
        total_fetched = 0
        inserted = 0
        updated = 0
        images_downloaded = 0
        errors_count = 0

        while True:
            page = await self._client.fetch_cards_page(
                num=page_size,
                offset=offset,
                misc=True,
            )
            cards = page.data
            if not cards:
                break

            meta = page.meta
            if total_expected is None and meta and meta.total_rows:
                total_expected = meta.total_rows
                await self._update_progress(job_id, total_expected=total_expected)

            for card in cards:
                try:
                    is_new, img_count = await self._process_card(
                        card,
                        api_db_version=api_version,
                    )
                    total_fetched += 1
                    if is_new:
                        inserted += 1
                    else:
                        updated += 1
                    images_downloaded += img_count
                except Exception as exc:  # noqa: BLE001
                    errors_count += 1
                    logger.warning("Card sync error passcode=%s: %s", card.id, exc)

                if total_fetched % 25 == 0:
                    await self._update_progress(
                        job_id,
                        total_fetched=total_fetched,
                        inserted=inserted,
                        updated=updated,
                        images_downloaded=images_downloaded,
                        errors_count=errors_count,
                    )

            if meta is None or meta.rows_remaining in (None, 0):
                break
            if meta.next_page_offset is not None:
                offset = meta.next_page_offset
            else:
                offset += len(cards)

        async with self._session_factory() as session:
            repo = CardRepository(session)
            job = await repo.get_job(job_id)
            if job:
                await repo.update_job(
                    job,
                    status=SyncJobStatus.COMPLETED.value,
                    api_db_version_after=api_version,
                    total_expected=total_expected or total_fetched,
                    total_fetched=total_fetched,
                    inserted=inserted,
                    updated=updated,
                    images_downloaded=images_downloaded,
                    errors_count=errors_count,
                    finished_at=datetime.now(timezone.utc),
                )
                await session.commit()

    async def _update_progress(self, job_id: int, **fields: int) -> None:
        async with self._session_factory() as session:
            repo = CardRepository(session)
            job = await repo.get_job(job_id)
            if job:
                await repo.update_job(job, **fields)
                await session.commit()

    async def _process_card(
        self,
        card: YgoCardApiSchema,
        *,
        api_db_version: str | None,
    ) -> tuple[bool, int]:
        async with self._session_factory() as session:
            repo = CardRepository(session)
            is_new = await repo.upsert_card_from_api(card, api_db_version=api_db_version)
            await session.commit()

        images_count = await self._download_card_images(card)
        return is_new, images_count

    async def _download_card_images(self, card: YgoCardApiSchema) -> int:
        card_dir = self._images_root / str(card.id)
        card_dir.mkdir(parents=True, exist_ok=True)
        downloaded = 0

        async with httpx.AsyncClient(timeout=60.0) as http:
            for image in card.card_images:
                local_path = None
                local_path_small = None
                local_path_cropped = None

                if image.image_url:
                    dest = card_dir / f"{image.id}.jpg"
                    if await self._download_file(http, image.image_url, dest):
                        local_path = f"{card.id}/{image.id}.jpg"
                        downloaded += 1
                    elif dest.exists():
                        local_path = f"{card.id}/{image.id}.jpg"

                if image.image_url_small:
                    dest = card_dir / f"{image.id}_small.jpg"
                    if await self._download_file(http, image.image_url_small, dest):
                        local_path_small = f"{card.id}/{image.id}_small.jpg"
                        downloaded += 1
                    elif dest.exists():
                        local_path_small = f"{card.id}/{image.id}_small.jpg"

                if image.image_url_cropped:
                    dest = card_dir / f"{image.id}_cropped.jpg"
                    if await self._download_file(http, image.image_url_cropped, dest):
                        local_path_cropped = f"{card.id}/{image.id}_cropped.jpg"
                        downloaded += 1
                    elif dest.exists():
                        local_path_cropped = f"{card.id}/{image.id}_cropped.jpg"

                if local_path or local_path_small or local_path_cropped:
                    async with self._session_factory() as session:
                        repo = CardRepository(session)
                        await repo.update_image_paths(
                            card.id,
                            image.id,
                            local_path=local_path,
                            local_path_small=local_path_small,
                            local_path_cropped=local_path_cropped,
                        )
                        await session.commit()

                await asyncio.sleep(0.05)

        return downloaded

    async def _download_file(
        self,
        client: httpx.AsyncClient,
        url: str,
        dest: Path,
    ) -> bool:
        if dest.exists() and dest.stat().st_size > 0:
            return False
        try:
            response = await client.get(url)
            response.raise_for_status()
            dest.write_bytes(response.content)
            return True
        except httpx.HTTPError as exc:
            logger.warning("Image download failed %s: %s", url, exc)
            return False

    async def get_stats(self) -> dict:
        async with self._session_factory() as session:
            repo = CardRepository(session)
            total = await repo.count_cards()
            last_job = await repo.get_latest_completed_job()
            processing = await repo.has_processing_job()
            return {
                "total_cards": total,
                "last_sync_at": last_job.finished_at if last_job else None,
                "api_db_version": last_job.api_db_version_after if last_job else None,
                "sync_in_progress": processing,
            }
