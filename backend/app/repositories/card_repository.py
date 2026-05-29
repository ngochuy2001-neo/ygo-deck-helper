"""Repository thao tác DB cho lá bài YGO."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.card import (
    SyncJobStatus,
    YgoCard,
    YgoCardImage,
    YgoCardPrice,
    YgoCardSet,
    YgoCardSyncJob,
)
from app.repositories.card_query_builder import build_order_by, build_search_filters
from app.schemas.card_search import CardSearchParams
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

    async def search_cards(
        self,
        params: CardSearchParams,
    ) -> tuple[list[YgoCard], dict[int, str], int]:
        """
        Danh sách lá bài có phân trang + bộ lọc đa tiêu chí.

        Returns:
            (cards, thumbnail_small_path_by_passcode, total_count)
        """
        filters = build_search_filters(params)

        count_stmt = select(func.count()).select_from(YgoCard)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int(await self._session.scalar(count_stmt) or 0)

        order_primary, order_secondary = build_order_by(params)
        stmt = (
            select(YgoCard)
            .order_by(order_primary, order_secondary)
            .offset(params.offset)
            .limit(params.limit)
        )
        if filters:
            stmt = stmt.where(*filters)
        cards = list((await self._session.scalars(stmt)).all())

        thumb_map: dict[int, str] = {}
        if cards:
            passcodes = [c.passcode for c in cards]
            img_stmt = (
                select(YgoCardImage)
                .where(
                    YgoCardImage.card_passcode.in_(passcodes),
                    YgoCardImage.local_path_small.isnot(None),
                )
                .order_by(
                    YgoCardImage.card_passcode,
                    YgoCardImage.is_default.desc(),
                    YgoCardImage.id,
                )
            )
            for img in (await self._session.scalars(img_stmt)).all():
                if img.card_passcode not in thumb_map and img.local_path_small:
                    thumb_map[img.card_passcode] = img.local_path_small

        return cards, thumb_map, total

    async def list_cards(
        self,
        *,
        query: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[YgoCard], dict[int, str], int]:
        """Backward-compatible wrapper — chỉ tìm theo tên."""
        from app.schemas.card_search import CardSearchParams, finalize_card_search

        params = finalize_card_search(
            CardSearchParams(q=query, offset=offset, limit=limit),
        )
        return await self.search_cards(params)

    async def get_filter_options(self) -> dict[str, list[str]]:
        """Giá trị distinct cho UI bộ lọc."""

        async def distinct_str(column: Any) -> list[str]:
            stmt = (
                select(column)
                .where(column.isnot(None))
                .distinct()
                .order_by(column)
            )
            return [str(row) for row in (await self._session.scalars(stmt)).all() if row]

        attributes = await distinct_str(YgoCard.attribute)

        monster_races_stmt = (
            select(YgoCard.race)
            .where(
                YgoCard.race.isnot(None),
                or_(
                    YgoCard.frame_type.is_(None),
                    YgoCard.frame_type.notin_(tuple(NON_MONSTER_FRAMES)),
                ),
            )
            .distinct()
            .order_by(YgoCard.race)
        )
        monster_races = [
            str(r)
            for r in (await self._session.scalars(monster_races_stmt)).all()
            if r
        ]

        spell_races_stmt = (
            select(YgoCard.race)
            .where(YgoCard.frame_type == "spell", YgoCard.race.isnot(None))
            .distinct()
            .order_by(YgoCard.race)
        )
        spell_races = [str(r) for r in (await self._session.scalars(spell_races_stmt)).all() if r]

        trap_races_stmt = (
            select(YgoCard.race)
            .where(YgoCard.frame_type == "trap", YgoCard.race.isnot(None))
            .distinct()
            .order_by(YgoCard.race)
        )
        trap_races = [str(r) for r in (await self._session.scalars(trap_races_stmt)).all() if r]

        frame_types_stmt = (
            select(YgoCard.frame_type)
            .where(
                YgoCard.frame_type.isnot(None),
                YgoCard.frame_type.notin_(("token", "skill")),
            )
            .distinct()
            .order_by(YgoCard.frame_type)
        )
        frame_types = [
            str(f) for f in (await self._session.scalars(frame_types_stmt)).all() if f
        ]

        archetypes_stmt = (
            select(YgoCard.archetype)
            .where(YgoCard.archetype.isnot(None))
            .distinct()
            .order_by(YgoCard.archetype)
            .limit(200)
        )
        archetypes_sample = [
            str(a) for a in (await self._session.scalars(archetypes_stmt)).all() if a
        ]

        linkmarkers: set[str] = set()
        markers_stmt = select(YgoCard.linkmarkers).where(YgoCard.linkmarkers.isnot(None))
        for raw in (await self._session.scalars(markers_stmt)).all():
            if isinstance(raw, list):
                linkmarkers.update(str(m) for m in raw)

        return {
            "attributes": attributes,
            "monster_races": monster_races,
            "spell_races": spell_races,
            "trap_races": trap_races,
            "linkmarkers": sorted(linkmarkers),
            "frame_types": frame_types,
            "archetypes_sample": archetypes_sample,
            "banlist_tcg_values": [
                "Forbidden",
                "Limited",
                "Semi-Limited",
                "Unlimited",
            ],
        }

    async def get_card_by_passcode(self, passcode: int) -> YgoCard | None:
        stmt = (
            select(YgoCard)
            .options(
                selectinload(YgoCard.card_sets),
                selectinload(YgoCard.card_images),
                selectinload(YgoCard.card_prices),
            )
            .where(YgoCard.passcode == passcode)
        )
        return await self._session.scalar(stmt)
