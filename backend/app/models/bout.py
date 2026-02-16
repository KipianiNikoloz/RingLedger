from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import BIGINT, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import BoutStatus, BoutWinner


class Bout(Base):
    __tablename__ = "bouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promoter_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fighter_a_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    fighter_b_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    event_datetime_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finish_after_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_after_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    show_a_drops: Mapped[int] = mapped_column(BIGINT, nullable=False)
    show_b_drops: Mapped[int] = mapped_column(BIGINT, nullable=False)
    bonus_a_drops: Mapped[int] = mapped_column(BIGINT, nullable=False)
    bonus_b_drops: Mapped[int] = mapped_column(BIGINT, nullable=False)

    status: Mapped[BoutStatus] = mapped_column(
        SAEnum(BoutStatus, name="bout_status", values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=BoutStatus.DRAFT,
    )
    winner: Mapped[BoutWinner | None] = mapped_column(
        SAEnum(BoutWinner, name="bout_winner", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

