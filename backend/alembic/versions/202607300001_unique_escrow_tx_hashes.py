"""enforce unique non-null escrow transaction hashes

Revision ID: 202607300001_unique_escrow_tx_hashes
Revises: 202602220000_baseline_schema
Create Date: 2026-07-30 16:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202607300001_unique_escrow_tx_hashes"
down_revision: str | None = "202602220000_baseline_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_escrows_create_tx_hash_not_null",
        "escrows",
        ["create_tx_hash"],
        unique=True,
        postgresql_where=sa.text("create_tx_hash IS NOT NULL"),
    )
    op.create_index(
        "uq_escrows_close_tx_hash_not_null",
        "escrows",
        ["close_tx_hash"],
        unique=True,
        postgresql_where=sa.text("close_tx_hash IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_escrows_close_tx_hash_not_null", table_name="escrows")
    op.drop_index("uq_escrows_create_tx_hash_not_null", table_name="escrows")
