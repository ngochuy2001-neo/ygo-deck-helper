"""rulebook RAG chunks with pgvector

Revision ID: 003
Revises: 002
Create Date: 2026-05-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

from app.core.config import settings

revision: str = "003"
down_revision: Union[str, None] = "002_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBED_DIM = settings.RAG_EMBEDDING_DIMENSION


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "rulebook_chunk_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chunk_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_headings", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("source_filename", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding", Vector(EMBED_DIM), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chunk_id", name="uq_rulebook_chunk_embeddings_chunk_id"),
    )
    op.create_index(
        "ix_rulebook_chunk_embeddings_chunk_id",
        "rulebook_chunk_embeddings",
        ["chunk_id"],
    )
    op.create_index(
        "ix_rulebook_chunk_embeddings_content_hash",
        "rulebook_chunk_embeddings",
        ["content_hash"],
    )
    op.execute(
        """
        CREATE INDEX ix_rulebook_chunk_embeddings_embedding_hnsw
        ON rulebook_chunk_embeddings
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_rulebook_chunk_embeddings_embedding_hnsw",
        table_name="rulebook_chunk_embeddings",
    )
    op.drop_index("ix_rulebook_chunk_embeddings_content_hash", table_name="rulebook_chunk_embeddings")
    op.drop_index("ix_rulebook_chunk_embeddings_chunk_id", table_name="rulebook_chunk_embeddings")
    op.drop_table("rulebook_chunk_embeddings")
