from __future__ import annotations

import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.db.uow import SqlAlchemyUnitOfWork
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository


class UnitOfWorkUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_exposes_selective_repositories(self) -> None:
        with Session(self.engine) as session:
            uow = SqlAlchemyUnitOfWork(session=session)
            self.assertIsInstance(uow.bouts, BoutRepository)
            self.assertIsInstance(uow.escrows, EscrowRepository)
            self.assertIsInstance(uow.idempotency_keys, IdempotencyKeyRepository)
            self.assertIsInstance(uow.audit_logs, AuditLogRepository)

    def test_commit_persists_pending_changes(self) -> None:
        user_id = uuid.uuid4()
        with Session(self.engine) as session:
            uow = SqlAlchemyUnitOfWork(session=session)
            session.add(
                User(
                    id=user_id,
                    email="uow.commit@example.test",
                    password_hash="pbkdf2_sha256$1$00$00",
                    role=UserRole.PROMOTER,
                )
            )
            uow.commit()

        with Session(self.engine) as session:
            persisted = session.get(User, user_id)
            self.assertIsNotNone(persisted)

    def test_rollback_discards_pending_changes(self) -> None:
        user_id = uuid.uuid4()
        with Session(self.engine) as session:
            uow = SqlAlchemyUnitOfWork(session=session)
            session.add(
                User(
                    id=user_id,
                    email="uow.rollback@example.test",
                    password_hash="pbkdf2_sha256$1$00$00",
                    role=UserRole.PROMOTER,
                )
            )
            uow.rollback()

        with Session(self.engine) as session:
            persisted = session.get(User, user_id)
            self.assertIsNone(persisted)


if __name__ == "__main__":
    unittest.main()
