from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.integrations.xrpl_client import XrplTransactionEvidence
from app.models.escrow import Escrow


class XrplEscrowValidationError(ValueError):
    """Raised when confirmed XRPL data does not satisfy expected escrow invariants."""


@dataclass(frozen=True)
class EscrowCreateConfirmation:
    tx_hash: str
    transaction_type: str
    offer_sequence: int
    validated: bool
    engine_result: str
    owner_address: str
    destination_address: str
    amount_drops: int
    finish_after_ripple: int
    cancel_after_ripple: int | None
    condition_hex: str | None


class EscrowPayoutAction(StrEnum):
    FINISH = "finish"
    CANCEL = "cancel"


@dataclass(frozen=True)
class EscrowPayoutConfirmation:
    tx_hash: str
    validated: bool
    engine_result: str
    transaction_type: str
    owner_address: str
    offer_sequence: int
    close_time_ripple: int
    fulfillment_hex: str | None


@dataclass(frozen=True)
class XrplEscrowService:
    @staticmethod
    def create_confirmation_from_evidence(evidence: XrplTransactionEvidence) -> EscrowCreateConfirmation:
        tx = evidence.tx_json
        return EscrowCreateConfirmation(
            tx_hash=evidence.tx_hash,
            transaction_type=_required_str(tx, "TransactionType"),
            offer_sequence=_required_int(tx, "Sequence"),
            validated=True,
            engine_result=evidence.engine_result,
            owner_address=_required_str(tx, "Account"),
            destination_address=_required_str(tx, "Destination"),
            amount_drops=_required_int(tx, "Amount"),
            finish_after_ripple=_required_int(tx, "FinishAfter"),
            cancel_after_ripple=_optional_int(tx, "CancelAfter"),
            condition_hex=_optional_str(tx, "Condition"),
        )

    @staticmethod
    def payout_confirmation_from_evidence(evidence: XrplTransactionEvidence) -> EscrowPayoutConfirmation:
        if evidence.close_time_ripple is None:
            raise XrplEscrowValidationError("ledger_close_time_missing")
        tx = evidence.tx_json
        return EscrowPayoutConfirmation(
            tx_hash=evidence.tx_hash,
            validated=True,
            engine_result=evidence.engine_result,
            transaction_type=_required_str(tx, "TransactionType"),
            owner_address=_required_str(tx, "Owner"),
            offer_sequence=_required_int(tx, "OfferSequence"),
            close_time_ripple=evidence.close_time_ripple,
            fulfillment_hex=_optional_str(tx, "Fulfillment"),
        )

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
    def build_escrow_finish_tx(*, escrow: Escrow, fulfillment_hex: str | None) -> dict[str, Any]:
        if escrow.offer_sequence is None:
            raise ValueError("escrow_offer_sequence_missing")
        tx: dict[str, Any] = {
            "TransactionType": "EscrowFinish",
            "Account": escrow.owner_address,
            "Owner": escrow.owner_address,
            "OfferSequence": escrow.offer_sequence,
        }
        normalized_fulfillment = _normalize_optional_hex(fulfillment_hex)
        if normalized_fulfillment is not None:
            tx["Fulfillment"] = normalized_fulfillment
        return tx

    @staticmethod
    def build_escrow_cancel_tx(escrow: Escrow) -> dict[str, Any]:
        if escrow.offer_sequence is None:
            raise ValueError("escrow_offer_sequence_missing")
        return {
            "TransactionType": "EscrowCancel",
            "Account": escrow.owner_address,
            "Owner": escrow.owner_address,
            "OfferSequence": escrow.offer_sequence,
        }

    @staticmethod
    def validate_escrow_create_confirmation(*, escrow: Escrow, confirmation: EscrowCreateConfirmation) -> None:
        if not confirmation.validated:
            raise XrplEscrowValidationError("ledger_tx_not_validated")
        if confirmation.engine_result != "tesSUCCESS":
            raise XrplEscrowValidationError("ledger_tx_not_success")
        if confirmation.transaction_type != "EscrowCreate":
            raise XrplEscrowValidationError("ledger_transaction_type_mismatch")
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

    @staticmethod
    def validate_payout_confirmation(
        *,
        escrow: Escrow,
        confirmation: EscrowPayoutConfirmation,
        expected_action: EscrowPayoutAction,
        expected_fulfillment_hex: str | None,
    ) -> None:
        if not confirmation.validated:
            raise XrplEscrowValidationError("ledger_tx_not_validated")
        if confirmation.engine_result != "tesSUCCESS":
            raise XrplEscrowValidationError("ledger_tx_not_success")
        if confirmation.owner_address != escrow.owner_address:
            raise XrplEscrowValidationError("ledger_owner_address_mismatch")
        if escrow.offer_sequence is None:
            raise XrplEscrowValidationError("escrow_offer_sequence_missing")
        if confirmation.offer_sequence != escrow.offer_sequence:
            raise XrplEscrowValidationError("ledger_offer_sequence_mismatch")

        if expected_action == EscrowPayoutAction.FINISH:
            if confirmation.transaction_type != "EscrowFinish":
                raise XrplEscrowValidationError("ledger_transaction_type_mismatch")
            if confirmation.close_time_ripple < escrow.finish_after_ripple:
                raise XrplEscrowValidationError("ledger_finish_before_allowed")
            _validate_fulfillment(
                expected_fulfillment_hex=expected_fulfillment_hex,
                provided_fulfillment_hex=confirmation.fulfillment_hex,
            )
            return

        if confirmation.transaction_type != "EscrowCancel":
            raise XrplEscrowValidationError("ledger_transaction_type_mismatch")
        if escrow.cancel_after_ripple is None:
            raise XrplEscrowValidationError("ledger_cancel_after_missing")
        if confirmation.close_time_ripple < escrow.cancel_after_ripple:
            raise XrplEscrowValidationError("ledger_cancel_before_allowed")

        provided_fulfillment = _normalize_optional_hex(confirmation.fulfillment_hex)
        if provided_fulfillment is not None:
            raise XrplEscrowValidationError("ledger_unexpected_fulfillment")


def _normalize_optional_hex(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


def _required_str(tx: dict[str, Any], field: str) -> str:
    value = tx.get(field)
    if not isinstance(value, str) or not value:
        raise XrplEscrowValidationError(f"ledger_{field.lower()}_invalid")
    return value


def _required_int(tx: dict[str, Any], field: str) -> int:
    value = tx.get(field)
    if isinstance(value, bool):
        raise XrplEscrowValidationError(f"ledger_{field.lower()}_invalid")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise XrplEscrowValidationError(f"ledger_{field.lower()}_invalid") from exc
    if parsed < 0:
        raise XrplEscrowValidationError(f"ledger_{field.lower()}_invalid")
    return parsed


def _optional_int(tx: dict[str, Any], field: str) -> int | None:
    return None if field not in tx else _required_int(tx, field)


def _optional_str(tx: dict[str, Any], field: str) -> str | None:
    if field not in tx:
        return None
    return _required_str(tx, field)


def _validate_fulfillment(*, expected_fulfillment_hex: str | None, provided_fulfillment_hex: str | None) -> None:
    expected_fulfillment = _normalize_optional_hex(expected_fulfillment_hex)
    provided_fulfillment = _normalize_optional_hex(provided_fulfillment_hex)
    if expected_fulfillment is None:
        if provided_fulfillment is not None:
            raise XrplEscrowValidationError("ledger_unexpected_fulfillment")
        return
    if provided_fulfillment != expected_fulfillment:
        raise XrplEscrowValidationError("ledger_fulfillment_mismatch")
