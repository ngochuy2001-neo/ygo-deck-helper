"""card search indexes

Revision ID: 002
Revises: 001
Create Date: 2026-05-29

"""

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_ygo_cards_frame_type", "ygo_cards", ["frame_type"])
    op.create_index("ix_ygo_cards_attribute", "ygo_cards", ["attribute"])
    op.create_index("ix_ygo_cards_level", "ygo_cards", ["level"])
    op.create_index("ix_ygo_cards_atk", "ygo_cards", ["atk"])
    op.create_index("ix_ygo_cards_def", "ygo_cards", ["def"])
    op.create_index("ix_ygo_cards_linkval", "ygo_cards", ["linkval"])
    op.create_index("ix_ygo_cards_scale", "ygo_cards", ["scale"])
    op.create_index("ix_ygo_cards_race", "ygo_cards", ["race"])


def downgrade() -> None:
    op.drop_index("ix_ygo_cards_race", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_scale", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_linkval", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_def", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_atk", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_level", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_attribute", table_name="ygo_cards")
    op.drop_index("ix_ygo_cards_frame_type", table_name="ygo_cards")
