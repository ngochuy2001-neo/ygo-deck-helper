"""Schemas cho tra cứu / hiển thị lá bài."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class CardListItem(BaseModel):
    passcode: int
    name: str
    type: str
    atk: int | None = None
    def_: int | None = Field(None, serialization_alias="def")
    level: int | None = None
    attribute: str | None = None
    race: str | None = None
    image_small_path: str | None = None

    model_config = {"populate_by_name": True}


class CardListResponse(BaseModel):
    items: list[CardListItem]
    total: int
    offset: int
    limit: int
    has_more: bool


class CardImageDto(BaseModel):
    image_passcode: int
    image_path: str | None = None
    image_small_path: str | None = None
    image_cropped_path: str | None = None
    is_default: bool


class CardSetDto(BaseModel):
    set_name: str
    set_code: str | None = None
    set_rarity: str | None = None
    set_price: Decimal | None = None


class CardPriceDto(BaseModel):
    cardmarket_price: Decimal | None = None
    tcgplayer_price: Decimal | None = None
    ebay_price: Decimal | None = None
    amazon_price: Decimal | None = None
    coolstuffinc_price: Decimal | None = None


class CardDetailResponse(BaseModel):
    passcode: int
    name: str
    type: str
    frame_type: str | None = None
    desc: str | None = None
    atk: int | None = None
    def_: int | None = Field(None, serialization_alias="def")
    level: int | None = None
    race: str | None = None
    attribute: str | None = None
    scale: int | None = None
    linkval: int | None = None
    linkmarkers: list[Any] | None = None
    archetype: str | None = None
    ygoprodeck_url: str | None = None
    banlist_info: dict[str, Any] | None = None
    synced_at: datetime | None = None
    image_path: str | None = None
    image_small_path: str | None = None
    images: list[CardImageDto] = Field(default_factory=list)
    card_sets: list[CardSetDto] = Field(default_factory=list)
    prices: CardPriceDto | None = None

    model_config = {"populate_by_name": True}
