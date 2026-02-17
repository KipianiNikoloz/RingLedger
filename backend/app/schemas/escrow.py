from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import BoutStatus, EscrowKind, EscrowStatus


class EscrowPrepareItem(BaseModel):
    escrow_id: str
    escrow_kind: EscrowKind
    unsigned_tx: dict[str, Any]


class EscrowPrepareResponse(BaseModel):
    bout_id: str
    escrows: list[EscrowPrepareItem]


class EscrowConfirmRequest(BaseModel):
    escrow_kind: EscrowKind
    tx_hash: str = Field(min_length=8, max_length=128)
    offer_sequence: int = Field(ge=1)
    validated: bool
    engine_result: str = Field(min_length=3, max_length=32)
    owner_address: str = Field(min_length=3, max_length=64)
    destination_address: str = Field(min_length=3, max_length=64)
    amount_drops: int = Field(ge=0)
    finish_after_ripple: int = Field(ge=0)
    cancel_after_ripple: int | None = Field(default=None, ge=0)
    condition_hex: str | None = Field(default=None, max_length=1024)


class EscrowConfirmResponse(BaseModel):
    bout_id: str
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    bout_status: BoutStatus
    tx_hash: str
    offer_sequence: int
