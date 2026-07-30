from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BoutStatus, BoutWinner, EscrowCloseAction, EscrowKind, EscrowStatus
from app.schemas.xaman import XamanSignRequestView


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
    xaman_sign_request: XamanSignRequestView | None = None


class PayoutPrepareResponse(BaseModel):
    bout_id: str
    bout_status: BoutStatus
    escrows: list[PayoutPrepareItem]


class PayoutConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    escrow_kind: EscrowKind
    tx_hash: str = Field(min_length=8, max_length=128)


class PayoutConfirmResponse(BaseModel):
    bout_id: str
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    bout_status: BoutStatus
    tx_hash: str
