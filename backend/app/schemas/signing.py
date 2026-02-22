from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import EscrowKind, EscrowStatus


class SigningReconcileRequest(BaseModel):
    escrow_kind: EscrowKind
    payload_id: str = Field(min_length=8, max_length=128)
    observed_status: str | None = Field(default=None, max_length=32)
    observed_tx_hash: str | None = Field(default=None, max_length=128)


class SigningReconcileResponse(BaseModel):
    bout_id: str
    escrow_id: str
    escrow_kind: EscrowKind
    escrow_status: EscrowStatus
    payload_id: str
    signing_status: str
    tx_hash: str | None = None
    failure_code: str | None = None
