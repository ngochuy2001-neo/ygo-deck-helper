"""ORM cho RAG Rulebook (pgvector)."""

from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


class RulebookChunkEmbedding(Base):
    """Một chunk Rulebook đã embed — dùng cho semantic search RAG."""

    __tablename__ = "rulebook_chunk_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_headings: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.RAG_EMBEDDING_DIMENSION),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
