from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.idempotency_key import IdempotencyKey


@dataclass
class IdempotencyKeyRepository:
    session: Session

    def get(self, *, scope: str, idempotency_key: str) -> IdempotencyKey | None:
        return self.session.scalar(
            select(IdempotencyKey).where(
                IdempotencyKey.scope == scope,
                IdempotencyKey.idempotency_key == idempotency_key,
            )
        )

    def add(self, *, idempotency_key: IdempotencyKey) -> None:
        self.session.add(idempotency_key)
