from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import BoutStatus, BoutWinner, EscrowCloseAction, EscrowKind, EscrowStatus


class BoutResultRequest(BaseModel):
    winner: BoutWinner


class BoutResultResponse(BaseModel):
    bout_id: str
    bout_status: BoutStatus
    winner: BoutWinner


class PayoutPrepareItem(BaseModel):
    escrow_id: str
    escrow_kind: EscrowKind
    action: EscrowCloseAction
    unsigned_tx: dict[str, Any]


class PayoutPrepareResponse(BaseModel):
    bout_id: str
    bout_status: BoutStatus
    escrows: list[PayoutPrepareItem]


class PayoutConfirmRequest(BaseModel):
    escrow_kind: EscrowKind
    tx_hash: str = Field(min_length=8, max_length=128)
    validated: bool
    engine_result: str = Field(min_length=3, max_length=32)
    transaction_type: str = Field(min_length=10, max_length=32)
    owner_address: str = Field(min_length=3, max_length=64)
    offer_sequence: int = Field(ge=1)
    close_time_ripple: int = Field(ge=0)
    fulfillment_hex: str | None = Field(default=None, max_length=4096)


class PayoutConfirmResponse(BaseModel):
    bout_id: str
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    bout_status: BoutStatus
    tx_hash: str
