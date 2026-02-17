from __future__ import annotations

import uuid

from fastapi import HTTPException, status


def require_idempotency_key(idempotency_key: str | None) -> str:
    if idempotency_key is None or not idempotency_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required.",
        )
    return idempotency_key.strip()


def build_confirm_scope(*, operation: str, bout_id: uuid.UUID) -> str:
    return f"{operation}:{bout_id}"
