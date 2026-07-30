from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BIGINT, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import EscrowKind, EscrowStatus


class Escrow(Base):
    __tablename__ = "escrows"
    __table_args__ = (
        UniqueConstraint("bout_id", "kind", name="uq_escrow_bout_kind"),
        Index(
            "uq_escrows_create_tx_hash_not_null",
            "create_tx_hash",
            unique=True,
            postgresql_where=text("create_tx_hash IS NOT NULL"),
            sqlite_where=text("create_tx_hash IS NOT NULL"),
        ),
        Index(
            "uq_escrows_close_tx_hash_not_null",
            "close_tx_hash",
            unique=True,
            postgresql_where=text("close_tx_hash IS NOT NULL"),
            sqlite_where=text("close_tx_hash IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bout_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bouts.id"), nullable=False, index=True)
    kind: Mapped[EscrowKind] = mapped_column(
        SAEnum(EscrowKind, name="escrow_kind", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    status: Mapped[EscrowStatus] = mapped_column(
        SAEnum(EscrowStatus, name="escrow_status", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=EscrowStatus.PLANNED,
        index=True,
    )

    owner_address: Mapped[str] = mapped_column(String(64), nullable=False)
    destination_address: Mapped[str] = mapped_column(String(64), nullable=False)
    amount_drops: Mapped[int] = mapped_column(BIGINT, nullable=False)

    finish_after_ripple: Mapped[int] = mapped_column(Integer, nullable=False)
    cancel_after_ripple: Mapped[int | None] = mapped_column(Integer, nullable=True)

    condition_hex: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    encrypted_preimage_hex: Mapped[str | None] = mapped_column(String(4096), nullable=True)

    offer_sequence: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    create_tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    close_tx_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
