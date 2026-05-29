"""Xây dựng điều kiện SQLAlchemy từ CardSearchParams."""

from __future__ import annotations

from typing import Any

from sqlalchemy import String, and_, cast, or_
from sqlalchemy.dialects.postgresql import ARRAY

from app.domain.card_filter_rules import NON_MONSTER_FRAMES, CardGroup
from app.models.card import YgoCard
from app.schemas.card_search import CardSearchParams, StatRange


def _apply_stat_range(column: Any, stat: StatRange | None) -> list[Any]:
    if stat is None:
        return []
    clauses: list[Any] = []
    if stat.min is not None:
        clauses.append(column >= stat.min)
    if stat.max is not None:
        clauses.append(column <= stat.max)
    return clauses


def build_search_filters(params: CardSearchParams) -> list[Any]:
    filters: list[Any] = []

    if params.passcode is not None:
        filters.append(YgoCard.passcode == params.passcode)
        return filters

    if params.q and params.q.strip():
        filters.append(YgoCard.name.ilike(f"%{params.q.strip()}%"))

    if params.card_group is not None:
        group = params.card_group
        if group == CardGroup.MONSTER:
            filters.append(
                or_(
                    YgoCard.frame_type.is_(None),
                    YgoCard.frame_type.notin_(tuple(NON_MONSTER_FRAMES)),
                ),
            )
        elif group == CardGroup.SPELL:
            filters.append(YgoCard.frame_type == "spell")
        elif group == CardGroup.TRAP:
            filters.append(YgoCard.frame_type == "trap")
        elif group == CardGroup.TOKEN:
            filters.append(YgoCard.frame_type == "token")
        elif group == CardGroup.SKILL:
            filters.append(YgoCard.frame_type == "skill")

    if params.frame_types:
        filters.append(YgoCard.frame_type.in_(params.frame_types))

    if params.attributes:
        filters.append(YgoCard.attribute.in_(params.attributes))

    if params.races:
        filters.append(YgoCard.race.in_(params.races))

    if params.spell_races:
        filters.append(
            and_(YgoCard.frame_type == "spell", YgoCard.race.in_(params.spell_races)),
        )

    if params.trap_races:
        filters.append(
            and_(YgoCard.frame_type == "trap", YgoCard.race.in_(params.trap_races)),
        )

    filters.extend(_apply_stat_range(YgoCard.level, params.level))
    filters.extend(_apply_stat_range(YgoCard.atk, params.atk))
    filters.extend(_apply_stat_range(YgoCard.def_, params.def_))
    filters.extend(_apply_stat_range(YgoCard.scale, params.scale))
    filters.extend(_apply_stat_range(YgoCard.linkval, params.linkval))

    if params.linkmarkers:
        filters.append(
            YgoCard.linkmarkers.bool_op("?|")(
                cast(params.linkmarkers, ARRAY(String)),
            ),
        )

    if params.archetype and params.archetype.strip():
        filters.append(YgoCard.archetype.ilike(f"%{params.archetype.strip()}%"))

    if params.banlist_tcg:
        tcg_filters = [
            YgoCard.banlist_info["ban_tcg"].astext == status
            for status in params.banlist_tcg
        ]
        if "Unlimited" in params.banlist_tcg:
            tcg_filters.append(
                or_(
                    YgoCard.banlist_info.is_(None),
                    YgoCard.banlist_info["ban_tcg"].astext.is_(None),
                ),
            )
        filters.append(or_(*tcg_filters))

    return filters


def build_order_by(params: CardSearchParams) -> Any:
    sort_col = {
        "name": YgoCard.name,
        "atk": YgoCard.atk,
        "def": YgoCard.def_,
        "level": YgoCard.level,
        "linkval": YgoCard.linkval,
        "passcode": YgoCard.passcode,
    }.get(params.sort, YgoCard.name)

    if params.order == "desc":
        return sort_col.desc().nulls_last(), YgoCard.passcode.asc()
    return sort_col.asc().nulls_last(), YgoCard.passcode.asc()
