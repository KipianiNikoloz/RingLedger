from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.escrow import Escrow


class XrplEscrowValidationError(ValueError):
    """Raised when confirmed XRPL data does not satisfy expected escrow invariants."""


@dataclass(frozen=True)
class EscrowCreateConfirmation:
    tx_hash: str
    offer_sequence: int
    validated: bool
    engine_result: str
    owner_address: str
    destination_address: str
    amount_drops: int
    finish_after_ripple: int
    cancel_after_ripple: int | None
    condition_hex: str | None


@dataclass(frozen=True)
class XrplEscrowService:
    @staticmethod
    def build_escrow_create_tx(escrow: Escrow) -> dict[str, Any]:
        tx: dict[str, Any] = {
            "TransactionType": "EscrowCreate",
            "Account": escrow.owner_address,
            "Destination": escrow.destination_address,
            "Amount": str(escrow.amount_drops),
            "FinishAfter": escrow.finish_after_ripple,
        }
        if escrow.cancel_after_ripple is not None:
            tx["CancelAfter"] = escrow.cancel_after_ripple
        if escrow.condition_hex is not None:
            tx["Condition"] = escrow.condition_hex
        return tx

    @staticmethod
    def validate_escrow_create_confirmation(*, escrow: Escrow, confirmation: EscrowCreateConfirmation) -> None:
        if not confirmation.validated:
            raise XrplEscrowValidationError("ledger_tx_not_validated")
        if confirmation.engine_result != "tesSUCCESS":
            raise XrplEscrowValidationError("ledger_tx_not_success")
        if confirmation.owner_address != escrow.owner_address:
            raise XrplEscrowValidationError("ledger_owner_address_mismatch")
        if confirmation.destination_address != escrow.destination_address:
            raise XrplEscrowValidationError("ledger_destination_address_mismatch")
        if confirmation.amount_drops != escrow.amount_drops:
            raise XrplEscrowValidationError("ledger_amount_mismatch")
        if confirmation.finish_after_ripple != escrow.finish_after_ripple:
            raise XrplEscrowValidationError("ledger_finish_after_mismatch")
        if confirmation.cancel_after_ripple != escrow.cancel_after_ripple:
            raise XrplEscrowValidationError("ledger_cancel_after_mismatch")

        expected_condition = _normalize_optional_hex(escrow.condition_hex)
        provided_condition = _normalize_optional_hex(confirmation.condition_hex)
        if provided_condition != expected_condition:
            raise XrplEscrowValidationError("ledger_condition_mismatch")


def _normalize_optional_hex(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None
