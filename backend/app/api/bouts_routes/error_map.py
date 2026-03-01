from __future__ import annotations

from typing import Any

from fastapi import status

_ESCROW_CREATE_CONFLICT_ERRORS = {
    "bout_not_in_draft_state",
    "escrow_not_planned",
}
_ESCROW_CREATE_UNPROCESSABLE_CONFIRMATION_ERRORS = {
    "invalid_confirmation",
    "signing_declined",
    "confirmation_timeout",
    "ledger_tec_tem",
    "ledger_not_success",
    "ledger_not_validated",
}
_RESULT_CONFLICT_ERRORS = {
    "bout_not_in_escrows_created_state",
}
_PAYOUT_PREPARE_CONFLICT_ERRORS = {
    "bout_not_preparable_for_payout",
    "escrow_not_preparable_for_payout",
    "bout_winner_not_set",
}
_PAYOUT_CONFIRM_CONFLICT_ERRORS = {
    "bout_not_in_payout_state",
    "escrow_not_created",
    "bout_winner_not_set",
}
_PAYOUT_UNPROCESSABLE_CONFIRMATION_ERRORS = {
    "invalid_confirmation",
    "signing_declined",
    "confirmation_timeout",
    "ledger_tec_tem",
    "ledger_not_success",
    "ledger_not_validated",
}
_SIGNING_RECONCILIATION_NOT_FOUND_ERRORS = {
    "bout_not_found",
    "escrow_not_found",
}

_CONFIRMATION_FAILURE_DETAILS: dict[str, str] = {
    "signing_declined": "Signing was declined; no state transition was applied.",
    "confirmation_timeout": "Confirmation timed out or remained unvalidated; no state transition was applied.",
    "ledger_tec_tem": "Ledger transaction was rejected with tec/tem; no state transition was applied.",
    "ledger_not_success": "Ledger transaction did not succeed; no state transition was applied.",
    "ledger_not_validated": "Ledger transaction was not validated; no state transition was applied.",
    "invalid_confirmation": "Ledger confirmation failed validation.",
}


def map_escrow_create_confirm_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in {"bout_not_found", "escrow_not_found"}:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code in _ESCROW_CREATE_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Escrow confirmation is not allowed in current state."}
    if error_code in _ESCROW_CREATE_UNPROCESSABLE_CONFIRMATION_ERRORS:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {
            "detail": _CONFIRMATION_FAILURE_DETAILS.get(error_code, "Ledger confirmation failed validation.")
        }
    return status.HTTP_400_BAD_REQUEST, {"detail": "Escrow confirmation request is invalid."}


def map_result_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code == "bout_not_found":
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout was not found."}
    if error_code in _RESULT_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Bout result cannot be entered in current state."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Bout result request is invalid."}


def map_payout_prepare_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code == "bout_not_found":
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout was not found."}
    if error_code in _PAYOUT_PREPARE_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Payout prepare is not allowed in current state."}
    if error_code in {"bout_escrow_set_invalid", "winner_bonus_fulfillment_missing"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Payout setup is invalid."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Payout prepare request is invalid."}


def map_payout_confirm_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in {"bout_not_found", "escrow_not_found"}:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code in _PAYOUT_CONFIRM_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Payout confirmation is not allowed in current state."}
    if error_code in _PAYOUT_UNPROCESSABLE_CONFIRMATION_ERRORS:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {
            "detail": _CONFIRMATION_FAILURE_DETAILS.get(error_code, "Ledger confirmation failed validation.")
        }
    if error_code in {"winner_bonus_fulfillment_missing", "bout_escrow_set_invalid"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Payout setup is invalid."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Payout confirmation request is invalid."}


def map_signing_reconcile_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in _SIGNING_RECONCILIATION_NOT_FOUND_ERRORS:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code == "xaman_observed_status_invalid":
        return status.HTTP_400_BAD_REQUEST, {"detail": "Observed signing status is invalid."}
    if error_code in {
        "xaman_mode_invalid",
        "xaman_api_credentials_missing",
        "xaman_api_http_error",
        "xaman_api_connection_error",
        "xaman_api_invalid_json",
        "xaman_api_invalid_response",
    }:
        return status.HTTP_502_BAD_GATEWAY, {"detail": "Xaman payload status could not be reconciled."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Signing reconciliation request is invalid."}
