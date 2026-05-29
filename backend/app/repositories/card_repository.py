"""Repository thao tác DB cho lá bài YGO."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import (
    SyncJobStatus,
    YgoCard,
    YgoCardImage,
    YgoCardPrice,
    YgoCardSet,
    YgoCardSyncJob,
)
from app.schemas.ygoprodeck import YgoCardApiSchema


def _parse_decimal(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


class CardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_cards(self) -> int:
        result = await self._session.scalar(select(func.count()).select_from(YgoCard))
        return int(result or 0)

    async def get_latest_completed_job(self) -> YgoCardSyncJob | None:
        stmt = (
            select(YgoCardSyncJob)
            .where(YgoCardSyncJob.status == SyncJobStatus.COMPLETED.value)
            .order_by(YgoCardSyncJob.finished_at.desc())
            .limit(1)
        )
        return await self._session.scalar(stmt)

    async def get_job(self, job_id: int) -> YgoCardSyncJob | None:
        return await self._session.get(YgoCardSyncJob, job_id)

    async def get_latest_job(self) -> YgoCardSyncJob | None:
        stmt = select(YgoCardSyncJob).order_by(YgoCardSyncJob.id.desc()).limit(1)
        return await self._session.scalar(stmt)

    async def has_processing_job(self) -> bool:
        stmt = select(func.count()).select_from(YgoCardSyncJob).where(
            YgoCardSyncJob.status == SyncJobStatus.PROCESSING.value
        )
        count = await self._session.scalar(stmt)
        return int(count or 0) > 0

    async def create_sync_job(self, *, force: bool) -> YgoCardSyncJob:
        job = YgoCardSyncJob(
            status=SyncJobStatus.PROCESSING.value,
            force=force,
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_job(self, job: YgoCardSyncJob, **fields: Any) -> YgoCardSyncJob:
        for key, value in fields.items():
            setattr(job, key, value)
        await self._session.flush()
        return job

    async def card_exists(self, passcode: int) -> bool:
        result = await self._session.scalar(
            select(func.count()).select_from(YgoCard).where(YgoCard.passcode == passcode)
        )
        return int(result or 0) > 0

    async def upsert_card_from_api(
        self,
        card: YgoCardApiSchema,
        *,
        api_db_version: str | None,
    ) -> bool:
        """Upsert lá bài; trả True nếu insert mới, False nếu update."""
        existed = await self.card_exists(card.id)
        banlist: dict[str, Any] | None = None
        if card.banlist_info is not None:
            if hasattr(card.banlist_info, "model_dump"):
                banlist = card.banlist_info.model_dump(exclude_none=True)
            elif isinstance(card.banlist_info, dict):
                banlist = card.banlist_info

        values = {
            "passcode": card.id,
            "name": card.name,
            "type": card.type,
            "frame_type": card.frameType,
            "desc": card.desc,
            "atk": card.atk,
            "def": card.def_,
            "level": card.level,
            "race": card.race,
            "attribute": card.attribute,
            "scale": card.scale,
            "linkval": card.linkval,
            "linkmarkers": card.linkmarkers,
            "archetype": card.archetype,
            "ygoprodeck_url": card.ygoprodeck_url,
            "banlist_info": banlist,
            "misc": card.misc,
            "api_db_version": api_db_version,
            "synced_at": datetime.now(timezone.utc),
        }
        stmt = insert(YgoCard).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["passcode"],
            set_={k: v for k, v in values.items() if k != "passcode"},
        )
        await self._session.execute(stmt)

        await self._session.execute(
            delete(YgoCardSet).where(YgoCardSet.card_passcode == card.id)
        )
        await self._session.execute(
            delete(YgoCardImage).where(YgoCardImage.card_passcode == card.id)
        )
        await self._session.execute(
            delete(YgoCardPrice).where(YgoCardPrice.card_passcode == card.id)
        )

        for card_set in card.card_sets:
            self._session.add(
                YgoCardSet(
                    card_passcode=card.id,
                    set_name=card_set.set_name,
                    set_code=card_set.set_code,
                    set_rarity=card_set.set_rarity,
                    set_rarity_code=card_set.set_rarity_code,
                    set_price=_parse_decimal(card_set.set_price),
                )
            )

        for idx, image in enumerate(card.card_images):
            self._session.add(
                YgoCardImage(
                    card_passcode=card.id,
                    image_passcode=image.id,
                    image_url=image.image_url,
                    image_url_small=image.image_url_small,
                    image_url_cropped=image.image_url_cropped,
                    is_default=idx == 0,
                )
            )

        if card.card_prices:
            price = card.card_prices[0]
            self._session.add(
                YgoCardPrice(
                    card_passcode=card.id,
                    cardmarket_price=_parse_decimal(price.cardmarket_price),
                    tcgplayer_price=_parse_decimal(price.tcgplayer_price),
                    ebay_price=_parse_decimal(price.ebay_price),
                    amazon_price=_parse_decimal(price.amazon_price),
                    coolstuffinc_price=_parse_decimal(price.coolstuffinc_price),
                )
            )

        return not existed

    async def update_image_paths(
        self,
        card_passcode: int,
        image_passcode: int,
        *,
        local_path: str | None = None,
        local_path_small: str | None = None,
        local_path_cropped: str | None = None,
    ) -> None:
        stmt = select(YgoCardImage).where(
            YgoCardImage.card_passcode == card_passcode,
            YgoCardImage.image_passcode == image_passcode,
        )
        image_row = await self._session.scalar(stmt)
        if image_row is None:
            return
        if local_path is not None:
            image_row.local_path = local_path
        if local_path_small is not None:
            image_row.local_path_small = local_path_small
        if local_path_cropped is not None:
            image_row.local_path_cropped = local_path_cropped
        await self._session.flush()
