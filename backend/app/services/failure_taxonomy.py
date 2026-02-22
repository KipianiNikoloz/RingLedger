from __future__ import annotations

_DECLINED_ENGINE_RESULTS = {
    "declined",
    "signing_declined",
    "user_declined",
    "xaman_declined",
    "cancelled",
    "canceled",
}
_TIMEOUT_ENGINE_RESULTS = {
    "timeout",
    "timed_out",
    "confirmation_timeout",
    "ledger_timeout",
    "tx_timeout",
}


def classify_confirmation_failure(
    *,
    validation_error: str,
    validated: bool,
    engine_result: str,
) -> str:
    normalized_result = engine_result.strip().lower()
    if normalized_result in _DECLINED_ENGINE_RESULTS or "declined" in normalized_result:
        return "signing_declined"
    if normalized_result in _TIMEOUT_ENGINE_RESULTS or "timeout" in normalized_result:
        return "confirmation_timeout"

    if validation_error == "ledger_tx_not_success":
        if normalized_result.startswith("tec") or normalized_result.startswith("tem"):
            return "ledger_tec_tem"
        return "ledger_not_success"

    if validation_error == "ledger_tx_not_validated":
        # Unvalidated confirmations are treated as timeout/unconfirmed failure class for retry handling.
        return "confirmation_timeout" if not validated else "ledger_not_validated"

    return "invalid_confirmation"


def build_failure_reason(
    *,
    validation_error: str,
    validated: bool,
    engine_result: str,
) -> str:
    return (
        f"validation_error={validation_error};validated={str(validated).lower()};engine_result={engine_result.strip()}"
    )
