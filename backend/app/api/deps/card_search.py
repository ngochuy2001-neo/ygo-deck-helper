"""Dependency parse query → CardSearchParams."""

from __future__ import annotations

from typing import Literal

from fastapi import Query

from app.domain.card_filter_rules import CardGroup
from app.schemas.card_search import (
    CardSearchParams,
    finalize_card_search,
    stat_range_from_query,
)


async def card_search_params(
    q: str | None = Query(default=None, max_length=200),
    passcode: int | None = Query(default=None, ge=1),
    card_group: CardGroup | None = Query(default=None),
    frame_types: str | None = Query(
        default=None,
        description="Comma-separated frame_type values",
    ),
    attributes: str | None = Query(default=None),
    races: str | None = Query(default=None),
    spell_races: str | None = Query(default=None),
    trap_races: str | None = Query(default=None),
    level_min: int | None = Query(default=None, ge=0, le=13),
    level_max: int | None = Query(default=None, ge=0, le=13),
    atk_min: int | None = Query(default=None, ge=0),
    atk_max: int | None = Query(default=None, ge=0),
    def_min: int | None = Query(default=None, ge=0),
    def_max: int | None = Query(default=None, ge=0),
    scale_min: int | None = Query(default=None, ge=0, le=13),
    scale_max: int | None = Query(default=None, ge=0, le=13),
    linkval_min: int | None = Query(default=None, ge=0, le=8),
    linkval_max: int | None = Query(default=None, ge=0, le=8),
    linkmarkers: str | None = Query(default=None),
    archetype: str | None = Query(default=None, max_length=128),
    banlist_tcg: str | None = Query(default=None),
    sort: Literal["name", "atk", "def", "level", "linkval", "passcode"] = Query(
        default="name",
    ),
    order: Literal["asc", "desc"] = Query(default="asc"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=40, ge=1, le=100),
) -> CardSearchParams:
    base = CardSearchParams(
        q=q,
        passcode=passcode,
        card_group=card_group,
        frame_types=frame_types,
        attributes=attributes,
        races=races,
        spell_races=spell_races,
        trap_races=trap_races,
        level=stat_range_from_query(level_min, level_max),
        atk=stat_range_from_query(atk_min, atk_max),
        def_=stat_range_from_query(def_min, def_max),
        scale=stat_range_from_query(scale_min, scale_max),
        linkval=stat_range_from_query(linkval_min, linkval_max),
        linkmarkers=linkmarkers,
        archetype=archetype,
        banlist_tcg=banlist_tcg,
        sort=sort,
        order=order,
        offset=offset,
        limit=limit,
    )
    return finalize_card_search(base)
