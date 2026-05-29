"""add total_expected to sync jobs

Revision ID: 002
Revises: 001
Create Date: 2026-05-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ygo_card_sync_jobs",
        sa.Column("total_expected", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ygo_card_sync_jobs", "total_expected")
