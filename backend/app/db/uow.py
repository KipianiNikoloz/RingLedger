from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository


@dataclass
class SqlAlchemyUnitOfWork:
    session: Session
    bouts: BoutRepository = field(init=False)
    escrows: EscrowRepository = field(init=False)
    idempotency_keys: IdempotencyKeyRepository = field(init=False)
    audit_logs: AuditLogRepository = field(init=False)

    def __post_init__(self) -> None:
        self.bouts = BoutRepository(session=self.session)
        self.escrows = EscrowRepository(session=self.session)
        self.idempotency_keys = IdempotencyKeyRepository(session=self.session)
        self.audit_logs = AuditLogRepository(session=self.session)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
