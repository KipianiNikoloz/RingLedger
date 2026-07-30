from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BoutStatus, EscrowKind, EscrowStatus
from app.schemas.xaman import XamanSignRequestView


class EscrowPrepareItem(BaseModel):
    escrow_id: str
    escrow_kind: EscrowKind
    unsigned_tx: dict[str, Any]
    xaman_sign_request: XamanSignRequestView | None = None


class EscrowPrepareResponse(BaseModel):
    bout_id: str
    escrows: list[EscrowPrepareItem]


class EscrowConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    escrow_kind: EscrowKind
    tx_hash: str = Field(min_length=8, max_length=128)


class EscrowConfirmResponse(BaseModel):
    bout_id: str
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    bout_status: BoutStatus
    tx_hash: str
    offer_sequence: int
