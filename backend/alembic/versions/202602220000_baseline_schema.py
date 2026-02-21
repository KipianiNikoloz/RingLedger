"""baseline_schema

Revision ID: 202602220000_baseline_schema
Revises:
Create Date: 2026-02-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "202602220000_baseline_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    user_role_enum = postgresql.ENUM("promoter", "fighter", "management", "admin", name="user_role")
    bout_status_enum = postgresql.ENUM(
        "draft",
        "ready_for_escrow",
        "escrows_created",
        "result_entered",
        "payouts_in_progress",
        "closed",
        name="bout_status",
    )
    escrow_kind_enum = postgresql.ENUM("show_a", "show_b", "bonus_a", "bonus_b", name="escrow_kind")
    escrow_status_enum = postgresql.ENUM("planned", "created", "finished", "cancelled", "failed", name="escrow_status")
    bout_winner_enum = postgresql.ENUM("A", "B", name="bout_winner")

    bind = op.get_bind()
    for enum_type in [user_role_enum, bout_status_enum, escrow_kind_enum, escrow_status_enum, bout_winner_enum]:
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "fighter_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("xrpl_address", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("xrpl_address"),
    )

    op.create_table(
        "bouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("promoter_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fighter_a_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fighter_b_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_datetime_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finish_after_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancel_after_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("show_a_drops", sa.BigInteger(), nullable=False),
        sa.Column("show_b_drops", sa.BigInteger(), nullable=False),
        sa.Column("bonus_a_drops", sa.BigInteger(), nullable=False),
        sa.Column("bonus_b_drops", sa.BigInteger(), nullable=False),
        sa.Column("status", bout_status_enum, server_default=sa.text("'draft'"), nullable=False),
        sa.Column("winner", bout_winner_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("show_a_drops >= 0", name="ck_bouts_show_a_drops_nonnegative"),
        sa.CheckConstraint("show_b_drops >= 0", name="ck_bouts_show_b_drops_nonnegative"),
        sa.CheckConstraint("bonus_a_drops >= 0", name="ck_bouts_bonus_a_drops_nonnegative"),
        sa.CheckConstraint("bonus_b_drops >= 0", name="ck_bouts_bonus_b_drops_nonnegative"),
        sa.CheckConstraint("fighter_a_user_id <> fighter_b_user_id", name="ck_bouts_fighters_distinct"),
        sa.ForeignKeyConstraint(["promoter_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["fighter_a_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["fighter_b_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "escrows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bout_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", escrow_kind_enum, nullable=False),
        sa.Column("status", escrow_status_enum, server_default=sa.text("'planned'"), nullable=False),
        sa.Column("owner_address", sa.String(length=64), nullable=False),
        sa.Column("destination_address", sa.String(length=64), nullable=False),
        sa.Column("amount_drops", sa.BigInteger(), nullable=False),
        sa.Column("finish_after_ripple", sa.Integer(), nullable=False),
        sa.Column("cancel_after_ripple", sa.Integer(), nullable=True),
        sa.Column("condition_hex", sa.String(length=1024), nullable=True),
        sa.Column("encrypted_preimage_hex", sa.String(length=4096), nullable=True),
        sa.Column("offer_sequence", sa.Integer(), nullable=True),
        sa.Column("create_tx_hash", sa.String(length=128), nullable=True),
        sa.Column("close_tx_hash", sa.String(length=128), nullable=True),
        sa.Column("failure_code", sa.String(length=64), nullable=True),
        sa.Column("failure_reason", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount_drops >= 0", name="ck_escrows_amount_drops_nonnegative"),
        sa.ForeignKeyConstraint(["bout_id"], ["bouts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bout_id", "kind", name="uq_escrow_bout_kind"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "idempotency_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=128), nullable=False),
        sa.Column("response_code", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope", "idempotency_key", name="uq_idempotency_scope_key"),
    )

    op.create_index("idx_bouts_promoter_user_id", "bouts", ["promoter_user_id"], unique=False)
    op.create_index("idx_bouts_event_datetime_utc", "bouts", ["event_datetime_utc"], unique=False)
    op.create_index("idx_bouts_status", "bouts", ["status"], unique=False)
    op.create_index("idx_escrows_bout_id", "escrows", ["bout_id"], unique=False)
    op.create_index("idx_escrows_status", "escrows", ["status"], unique=False)
    op.create_index("idx_escrows_owner_offer_sequence", "escrows", ["owner_address", "offer_sequence"], unique=False)
    op.create_index("idx_fighter_profiles_xrpl_address", "fighter_profiles", ["xrpl_address"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_fighter_profiles_xrpl_address", table_name="fighter_profiles")
    op.drop_index("idx_escrows_owner_offer_sequence", table_name="escrows")
    op.drop_index("idx_escrows_status", table_name="escrows")
    op.drop_index("idx_escrows_bout_id", table_name="escrows")
    op.drop_index("idx_bouts_status", table_name="bouts")
    op.drop_index("idx_bouts_event_datetime_utc", table_name="bouts")
    op.drop_index("idx_bouts_promoter_user_id", table_name="bouts")

    op.drop_table("idempotency_keys")
    op.drop_table("audit_log")
    op.drop_table("escrows")
    op.drop_table("bouts")
    op.drop_table("fighter_profiles")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS bout_winner")
    op.execute("DROP TYPE IF EXISTS escrow_status")
    op.execute("DROP TYPE IF EXISTS escrow_kind")
    op.execute("DROP TYPE IF EXISTS bout_status")
    op.execute("DROP TYPE IF EXISTS user_role")
