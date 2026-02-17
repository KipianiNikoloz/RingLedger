from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.idempotency_key import IdempotencyKey


class IdempotencyKeyMismatchError(ValueError):
    """Raised when an idempotency key is reused with a different request payload."""


@dataclass(frozen=True)
class IdempotencyReplay:
    status_code: int
    response_body: dict[str, Any]


@dataclass
class IdempotencyService:
    session: Session

    @staticmethod
    def hash_request_payload(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def load_replay(
        self,
        *,
        scope: str,
        idempotency_key: str,
        request_hash: str,
    ) -> IdempotencyReplay | None:
        existing = self.session.scalar(
            select(IdempotencyKey).where(
                IdempotencyKey.scope == scope,
                IdempotencyKey.idempotency_key == idempotency_key,
            )
        )
        if existing is None:
            return None
        if existing.request_hash != request_hash:
            raise IdempotencyKeyMismatchError("idempotency_key_reused_with_different_payload")

        body = json.loads(existing.response_body)
        if not isinstance(body, dict):
            raise ValueError("idempotency_response_body_must_be_json_object")
        return IdempotencyReplay(status_code=existing.response_code, response_body=body)

    def store_response(
        self,
        *,
        scope: str,
        idempotency_key: str,
        request_hash: str,
        status_code: int,
        response_body: dict[str, Any],
    ) -> None:
        self.session.add(
            IdempotencyKey(
                scope=scope,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_code=status_code,
                response_body=json.dumps(response_body, separators=(",", ":"), sort_keys=True, ensure_ascii=True),
            )
        )
