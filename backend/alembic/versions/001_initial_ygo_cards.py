"""initial ygo cards schema

Revision ID: 001
Revises:
Create Date: 2026-05-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ygo_cards",
        sa.Column("passcode", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("frame_type", sa.String(length=32), nullable=True),
        sa.Column("desc", sa.Text(), nullable=True),
        sa.Column("atk", sa.Integer(), nullable=True),
        sa.Column("def", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("race", sa.String(length=64), nullable=True),
        sa.Column("attribute", sa.String(length=16), nullable=True),
        sa.Column("scale", sa.Integer(), nullable=True),
        sa.Column("linkval", sa.Integer(), nullable=True),
        sa.Column("linkmarkers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("archetype", sa.String(length=128), nullable=True),
        sa.Column("ygoprodeck_url", sa.String(length=512), nullable=True),
        sa.Column("banlist_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("misc", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("api_db_version", sa.String(length=64), nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("passcode"),
    )
    op.create_index("ix_ygo_cards_name", "ygo_cards", ["name"])
    op.create_index("ix_ygo_cards_archetype", "ygo_cards", ["archetype"])

    op.create_table(
        "ygo_card_sets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_passcode", sa.BigInteger(), nullable=False),
        sa.Column("set_name", sa.String(length=255), nullable=False),
        sa.Column("set_code", sa.String(length=32), nullable=True),
        sa.Column("set_rarity", sa.String(length=64), nullable=True),
        sa.Column("set_rarity_code", sa.String(length=16), nullable=True),
        sa.Column("set_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.ForeignKeyConstraint(["card_passcode"], ["ygo_cards.passcode"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ygo_card_sets_card_passcode", "ygo_card_sets", ["card_passcode"])

    op.create_table(
        "ygo_card_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_passcode", sa.BigInteger(), nullable=False),
        sa.Column("image_passcode", sa.BigInteger(), nullable=False),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("image_url_small", sa.String(length=512), nullable=True),
        sa.Column("image_url_cropped", sa.String(length=512), nullable=True),
        sa.Column("local_path", sa.String(length=512), nullable=True),
        sa.Column("local_path_small", sa.String(length=512), nullable=True),
        sa.Column("local_path_cropped", sa.String(length=512), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["card_passcode"], ["ygo_cards.passcode"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ygo_card_images_card_passcode", "ygo_card_images", ["card_passcode"])

    op.create_table(
        "ygo_card_prices",
        sa.Column("card_passcode", sa.BigInteger(), nullable=False),
        sa.Column("cardmarket_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("tcgplayer_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("ebay_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("amazon_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("coolstuffinc_price", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.ForeignKeyConstraint(["card_passcode"], ["ygo_cards.passcode"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("card_passcode"),
    )

    op.create_table(
        "ygo_card_sync_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("force", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("api_db_version_before", sa.String(length=64), nullable=True),
        sa.Column("api_db_version_after", sa.String(length=64), nullable=True),
        sa.Column("total_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("images_downloaded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ygo_card_sync_jobs_status", "ygo_card_sync_jobs", ["status"])


def downgrade() -> None:
    op.drop_table("ygo_card_sync_jobs")
    op.drop_table("ygo_card_prices")
    op.drop_table("ygo_card_images")
    op.drop_table("ygo_card_sets")
    op.drop_index("ix_ygo_cards_archetype", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_name", table_name="ygo_cards")
    op.drop_table("ygo_cards")
