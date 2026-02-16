from __future__ import annotations

from datetime import UTC, datetime, timedelta

RIPPLE_EPOCH_OFFSET = 946_684_800


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime_must_be_timezone_aware")
    return dt.astimezone(UTC)


def unix_to_ripple_epoch(unix_seconds: int) -> int:
    return unix_seconds - RIPPLE_EPOCH_OFFSET


def ripple_epoch_to_unix(ripple_seconds: int) -> int:
    return ripple_seconds + RIPPLE_EPOCH_OFFSET


def to_ripple_epoch(dt: datetime) -> int:
    utc = ensure_utc(dt)
    return unix_to_ripple_epoch(int(utc.timestamp()))


def from_ripple_epoch(ripple_seconds: int) -> datetime:
    unix_seconds = ripple_epoch_to_unix(ripple_seconds)
    return datetime.fromtimestamp(unix_seconds, tz=UTC)


def compute_finish_after(event_datetime_utc: datetime) -> datetime:
    return ensure_utc(event_datetime_utc) + timedelta(hours=2)


def compute_bonus_cancel_after(event_datetime_utc: datetime) -> datetime:
    return ensure_utc(event_datetime_utc) + timedelta(days=7)

