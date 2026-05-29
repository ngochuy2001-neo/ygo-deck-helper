"""ORM models cho lá bài Yu-Gi-Oh! (YGOPRODeck API v7)."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass


class SyncJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class YgoCard(Base):
    __tablename__ = "ygo_cards"

    passcode: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    frame_type: Mapped[str | None] = mapped_column(String(32))
    desc: Mapped[str | None] = mapped_column(Text)
    atk: Mapped[int | None] = mapped_column(Integer)
    def_: Mapped[int | None] = mapped_column("def", Integer)
    level: Mapped[int | None] = mapped_column(Integer)
    race: Mapped[str | None] = mapped_column(String(64))
    attribute: Mapped[str | None] = mapped_column(String(16))
    scale: Mapped[int | None] = mapped_column(Integer)
    linkval: Mapped[int | None] = mapped_column(Integer)
    linkmarkers: Mapped[list[Any] | None] = mapped_column(JSONB)
    archetype: Mapped[str | None] = mapped_column(String(128), index=True)
    ygoprodeck_url: Mapped[str | None] = mapped_column(String(512))
    banlist_info: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    misc: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    api_db_version: Mapped[str | None] = mapped_column(String(64))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    card_sets: Mapped[list[YgoCardSet]] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
    )
    card_images: Mapped[list[YgoCardImage]] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
    )
    card_prices: Mapped[YgoCardPrice | None] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
        uselist=False,
    )


class YgoCardSet(Base):
    __tablename__ = "ygo_card_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_passcode: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ygo_cards.passcode", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    set_name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_code: Mapped[str | None] = mapped_column(String(32))
    set_rarity: Mapped[str | None] = mapped_column(String(64))
    set_rarity_code: Mapped[str | None] = mapped_column(String(16))
    set_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))

    card: Mapped[YgoCard] = relationship(back_populates="card_sets")


class YgoCardImage(Base):
    __tablename__ = "ygo_card_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_passcode: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ygo_cards.passcode", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_passcode: Mapped[int] = mapped_column(BigInteger, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512))
    image_url_small: Mapped[str | None] = mapped_column(String(512))
    image_url_cropped: Mapped[str | None] = mapped_column(String(512))
    local_path: Mapped[str | None] = mapped_column(String(512))
    local_path_small: Mapped[str | None] = mapped_column(String(512))
    local_path_cropped: Mapped[str | None] = mapped_column(String(512))
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    card: Mapped[YgoCard] = relationship(back_populates="card_images")


class YgoCardPrice(Base):
    __tablename__ = "ygo_card_prices"

    card_passcode: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ygo_cards.passcode", ondelete="CASCADE"),
        primary_key=True,
    )
    cardmarket_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    tcgplayer_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ebay_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    amazon_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    coolstuffinc_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))

    card: Mapped[YgoCard] = relationship(back_populates="card_prices")


class YgoCardSyncJob(Base):
    __tablename__ = "ygo_card_sync_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SyncJobStatus.PENDING.value,
        index=True,
    )
    force: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    api_db_version_before: Mapped[str | None] = mapped_column(String(64))
    api_db_version_after: Mapped[str | None] = mapped_column(String(64))
    total_expected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    images_downloaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
