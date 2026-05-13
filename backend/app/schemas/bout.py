from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import BoutStatus, BoutWinner, EscrowKind, EscrowStatus
from app.schemas.fighter import XRPL_CLASSIC_ADDRESS_PATTERN


class BoutCreateRequest(BaseModel):
    fighter_a_user_id: uuid.UUID
    fighter_b_user_id: uuid.UUID
    event_datetime_utc: datetime
    promoter_owner_address: str = Field(min_length=25, max_length=35, pattern=XRPL_CLASSIC_ADDRESS_PATTERN)
    show_a_drops: int = Field(gt=0)
    show_b_drops: int = Field(gt=0)
    bonus_a_drops: int = Field(gt=0)
    bonus_b_drops: int = Field(gt=0)


class BoutEscrowSummary(BaseModel):
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    owner_address: str
    destination_address: str
    amount_drops: int
    offer_sequence: int | None = None
    create_tx_hash: str | None = None
    close_tx_hash: str | None = None


class BoutSummaryResponse(BaseModel):
    bout_id: str
    promoter_user_id: str
    fighter_a_user_id: str
    fighter_b_user_id: str
    event_datetime_utc: datetime
    finish_after_utc: datetime
    cancel_after_utc: datetime
    show_a_drops: int
    show_b_drops: int
    bonus_a_drops: int
    bonus_b_drops: int
    bout_status: BoutStatus
    winner: BoutWinner | None = None
    escrows: list[BoutEscrowSummary]


class BoutListResponse(BaseModel):
    bouts: list[BoutSummaryResponse]
