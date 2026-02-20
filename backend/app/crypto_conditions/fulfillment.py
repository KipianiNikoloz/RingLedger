from __future__ import annotations

import hashlib
import secrets


def generate_preimage_hex() -> str:
    # MVP invariant: secure, unique 32-byte preimage for each bonus escrow.
    return secrets.token_hex(32).upper()


def make_condition_hex(preimage_hex: str) -> str:
    raw = bytes.fromhex(_normalize_hex(preimage_hex))
    return hashlib.sha256(raw).hexdigest().upper()


def make_fulfillment_hex(preimage_hex: str) -> str:
    # Fulfillment transport format for MVP is normalized preimage hex.
    return _normalize_hex(preimage_hex)


def verify_fulfillment(*, condition_hex: str, fulfillment_hex: str) -> bool:
    return make_condition_hex(fulfillment_hex) == _normalize_hex(condition_hex)


def _normalize_hex(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError("hex_value_required")
    if len(normalized) % 2 != 0:
        raise ValueError("hex_value_must_have_even_length")
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise ValueError("hex_value_invalid") from exc
    return normalized
