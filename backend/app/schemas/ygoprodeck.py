"""Pydantic schemas cho response YGOPRODeck API v7."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class YgoCardSetSchema(BaseModel):
    set_name: str
    set_code: str | None = None
    set_rarity: str | None = None
    set_rarity_code: str | None = None
    set_price: str | None = None


class YgoCardImageSchema(BaseModel):
    id: int
    image_url: str | None = None
    image_url_small: str | None = None
    image_url_cropped: str | None = None


class YgoCardPriceSchema(BaseModel):
    cardmarket_price: str | None = None
    tcgplayer_price: str | None = None
    ebay_price: str | None = None
    amazon_price: str | None = None
    coolstuffinc_price: str | None = None


class YgoBanlistInfoSchema(BaseModel):
    ban_tcg: str | None = None
    ban_ocg: str | None = None
    ban_goat: str | None = None


class YgoCardApiSchema(BaseModel):
    id: int
    name: str
    type: str
    frameType: str | None = None
    desc: str | None = None
    atk: int | None = None
    def_: int | None = Field(None, alias="def")
    level: int | None = None
    race: str | None = None
    attribute: str | None = None
    scale: int | None = None
    linkval: int | None = None
    linkmarkers: list[str] | None = None
    archetype: str | None = None
    ygoprodeck_url: str | None = None
    card_sets: list[YgoCardSetSchema] = Field(default_factory=list)
    card_images: list[YgoCardImageSchema] = Field(default_factory=list)
    card_prices: list[YgoCardPriceSchema] = Field(default_factory=list)
    banlist_info: YgoBanlistInfoSchema | dict[str, Any] | None = None
    misc: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


class YgoCardInfoMeta(BaseModel):
    current_rows: int | None = None
    total_rows: int | None = None
    rows_remaining: int | None = None
    total_pages: int | None = None
    pages_remaining: int | None = None
    next_page: str | None = None
    next_page_offset: int | None = None


class YgoCardInfoResponse(BaseModel):
    data: list[YgoCardApiSchema] = Field(default_factory=list)
    meta: YgoCardInfoMeta | None = None


class YgoDbVersionResponse(BaseModel):
    database_version: str | int | float
    last_update: str | None = None
