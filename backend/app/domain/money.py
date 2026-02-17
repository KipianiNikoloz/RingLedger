from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

DROP_SCALE = Decimal("1000000")
MAX_DROPS = 9_223_372_036_854_775_807  # signed BIGINT max


def ensure_valid_drops(value: int) -> int:
    if not isinstance(value, int):
        raise TypeError("drops_must_be_int")
    if value < 0:
        raise ValueError("drops_must_be_non_negative")
    if value > MAX_DROPS:
        raise ValueError("drops_overflow_bigint")
    return value


def xrp_to_drops(xrp: str | Decimal) -> int:
    amount = Decimal(xrp)
    if amount < 0:
        raise ValueError("xrp_must_be_non_negative")
    drops = (amount * DROP_SCALE).quantize(Decimal("1"), rounding=ROUND_DOWN)
    if drops != amount * DROP_SCALE:
        raise ValueError("xrp_must_map_to_integer_drops")
    return ensure_valid_drops(int(drops))


def drops_to_xrp(drops: int) -> Decimal:
    clean_drops = ensure_valid_drops(drops)
    return Decimal(clean_drops) / DROP_SCALE
