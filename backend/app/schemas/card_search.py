"""Schemas tìm kiếm / lọc lá bài."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.card_filter_rules import CardGroup, sanitize_search_params


class StatRange(BaseModel):
    min: int | None = Field(default=None, ge=0)
    max: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def min_lte_max(self) -> StatRange:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min phải <= max")
        return self


class CardSearchParams(BaseModel):
    q: str | None = Field(default=None, max_length=200)
    passcode: int | None = Field(default=None, ge=1)
    card_group: CardGroup | None = None
    frame_types: list[str] | None = None
    attributes: list[str] | None = None
    races: list[str] | None = None
    spell_races: list[str] | None = None
    trap_races: list[str] | None = None
    level: StatRange | None = None
    atk: StatRange | None = None
    def_: StatRange | None = Field(default=None, alias="def")
    scale: StatRange | None = None
    linkval: StatRange | None = None
    linkmarkers: list[str] | None = None
    archetype: str | None = Field(default=None, max_length=128)
    banlist_tcg: list[str] | None = None
    sort: Literal["name", "atk", "def", "level", "linkval", "passcode"] = "name"
    order: Literal["asc", "desc"] = "asc"
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=40, ge=1, le=100)

    model_config = {"populate_by_name": True}

    @field_validator("frame_types", mode="before")
    @classmethod
    def normalize_frames(cls, v: list[str] | str | None) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            parts = [p.strip().lower() for p in v.split(",") if p.strip()]
            return parts or None
        return [str(x).lower() for x in v]

    @field_validator(
        "attributes",
        "races",
        "spell_races",
        "trap_races",
        "linkmarkers",
        "banlist_tcg",
        mode="before",
    )
    @classmethod
    def split_csv_lists(cls, v: list[str] | str | None) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return parts or None
        return list(v)

class CardFilterOptionsResponse(BaseModel):
    attributes: list[str]
    monster_races: list[str]
    spell_races: list[str]
    trap_races: list[str]
    linkmarkers: list[str]
    frame_types: list[str]
    archetypes_sample: list[str]
    banlist_tcg_values: list[str]


def stat_range_from_query(
    min_val: int | None,
    max_val: int | None,
) -> StatRange | None:
    if min_val is None and max_val is None:
        return None
    return StatRange(min=min_val, max=max_val)


def finalize_card_search(params: CardSearchParams) -> CardSearchParams:
    """Áp dụng quy tắc YGO sau khi parse query (gọi từ API layer)."""
    if params.passcode is not None:
        return CardSearchParams(
            passcode=params.passcode,
            sort=params.sort,
            order=params.order,
            offset=params.offset,
            limit=params.limit,
        )

    raw = params.model_dump(by_alias=True)
    if params.card_group == CardGroup.ALL:
        raw["card_group"] = None
    cleaned = sanitize_search_params(raw)
    return CardSearchParams.model_validate(cleaned)
