from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.models.audit_log import AuditLog
from app.models.bout import Bout
from app.models.enums import EscrowKind, EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.idempotency_key import IdempotencyKey
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository


class PersistenceRepositoriesUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_targeted_repositories_support_bout_escrow_audit_idempotency_paths(self) -> None:
        with Session(self.engine) as session:
            self._seed_users(session)

            bout_repo = BoutRepository(session=session)
            escrow_repo = EscrowRepository(session=session)
            audit_repo = AuditLogRepository(session=session)
            idempotency_repo = IdempotencyKeyRepository(session=session)

            bout = self._build_bout()
            bout_repo.add(bout=bout)
            session.flush()
            self.assertIsNotNone(bout_repo.get(bout_id=bout.id))

            escrows = self._build_escrows(bout_id=bout.id)
            escrow_repo.add_many(escrows=escrows)
            session.flush()

            loaded_for_bout = escrow_repo.list_for_bout(bout_id=bout.id)
            self.assertEqual(len(loaded_for_bout), 4)
            loaded_show_a = escrow_repo.get_for_bout_kind(bout_id=bout.id, escrow_kind=EscrowKind.SHOW_A)
            self.assertIsNotNone(loaded_show_a)

            idempotency = IdempotencyKey(
                scope=f"escrow_create_confirm:{bout.id}",
                idempotency_key="repo-key-1",
                request_hash="hash-1",
                response_code=200,
                response_body='{"detail":"ok"}',
            )
            idempotency_repo.add(idempotency_key=idempotency)
            session.flush()
            loaded_key = idempotency_repo.get(
                scope=f"escrow_create_confirm:{bout.id}",
                idempotency_key="repo-key-1",
            )
            self.assertIsNotNone(loaded_key)

            audit_repo.add(
                audit_log=AuditLog(
                    actor_user_id=None,
                    action="repository_test",
                    entity_type="bout",
                    entity_id=str(bout.id),
                    outcome="success",
                    details_json='{"detail":"ok"}',
                )
            )
            session.flush()
            persisted_audit = session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "repository_test",
                    AuditLog.entity_id == str(bout.id),
                )
            )
            self.assertIsNotNone(persisted_audit)

    @staticmethod
    def _seed_users(session: Session) -> None:
        session.add_all(
            [
                User(
                    id=uuid.UUID("00000000-0000-0000-0000-0000000000A1"),
                    email="repo.promoter@example.test",
                    password_hash="pbkdf2_sha256$1$00$00",
                    role=UserRole.PROMOTER,
                ),
                User(
                    id=uuid.UUID("00000000-0000-0000-0000-0000000000A2"),
                    email="repo.fighter.a@example.test",
                    password_hash="pbkdf2_sha256$1$00$00",
                    role=UserRole.FIGHTER,
                ),
                User(
                    id=uuid.UUID("00000000-0000-0000-0000-0000000000A3"),
                    email="repo.fighter.b@example.test",
                    password_hash="pbkdf2_sha256$1$00$00",
                    role=UserRole.FIGHTER,
                ),
            ]
        )
        session.flush()

    @staticmethod
    def _build_bout() -> Bout:
        event = datetime(2026, 2, 20, 10, 0, 0, tzinfo=UTC)
        return Bout(
            promoter_user_id=uuid.UUID("00000000-0000-0000-0000-0000000000A1"),
            fighter_a_user_id=uuid.UUID("00000000-0000-0000-0000-0000000000A2"),
            fighter_b_user_id=uuid.UUID("00000000-0000-0000-0000-0000000000A3"),
            event_datetime_utc=event,
            finish_after_utc=event,
            cancel_after_utc=event,
            show_a_drops=1_000_000,
            show_b_drops=1_000_000,
            bonus_a_drops=100_000,
            bonus_b_drops=100_000,
        )

    @staticmethod
    def _build_escrows(*, bout_id: uuid.UUID) -> list[Escrow]:
        return [
            Escrow(
                bout_id=bout_id,
                kind=EscrowKind.SHOW_A,
                status=EscrowStatus.PLANNED,
                owner_address="rPromoterRepo",
                destination_address="rFighterARepo",
                amount_drops=1_000_000,
                finish_after_ripple=1,
                cancel_after_ripple=None,
            ),
            Escrow(
                bout_id=bout_id,
                kind=EscrowKind.SHOW_B,
                status=EscrowStatus.PLANNED,
                owner_address="rPromoterRepo",
                destination_address="rFighterBRepo",
                amount_drops=1_000_000,
                finish_after_ripple=1,
                cancel_after_ripple=None,
            ),
            Escrow(
                bout_id=bout_id,
                kind=EscrowKind.BONUS_A,
                status=EscrowStatus.PLANNED,
                owner_address="rPromoterRepo",
                destination_address="rFighterARepo",
                amount_drops=100_000,
                finish_after_ripple=1,
                cancel_after_ripple=2,
                condition_hex="AA",
                encrypted_preimage_hex="BB",
            ),
            Escrow(
                bout_id=bout_id,
                kind=EscrowKind.BONUS_B,
                status=EscrowStatus.PLANNED,
                owner_address="rPromoterRepo",
                destination_address="rFighterBRepo",
                amount_drops=100_000,
                finish_after_ripple=1,
                cancel_after_ripple=2,
                condition_hex="CC",
                encrypted_preimage_hex="DD",
            ),
        ]


if __name__ == "__main__":
    unittest.main()
