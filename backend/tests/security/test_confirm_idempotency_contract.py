from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.enums import EscrowKind, UserRole
from app.models.escrow import Escrow
from app.models.user import User
from app.services.bout_service import BoutService


class ConfirmIdempotencySecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        self.bout_id, self.promoter_user_id, self.promoter_email = self._seed_bout()

        self.init_db_patcher = patch("app.main.init_db")
        self.init_db_patcher.start()
        self.app = create_app()
        self.app.dependency_overrides[get_session] = self._override_get_session
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        self.init_db_patcher.stop()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_confirm_requires_idempotency_key_header(self) -> None:
        payload = self._confirm_payload()
        response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers(),
            json=payload,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Idempotency-Key header is required.")

    def _override_get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def _seed_bout(self) -> tuple[uuid.UUID, uuid.UUID, str]:
        with Session(self.engine) as session:
            promoter_email = "promoter.security@example.test"
            promoter_id = self._insert_user(session, promoter_email, UserRole.PROMOTER)
            fighter_a_id = self._insert_user(session, "fighter.security.a@example.test", UserRole.FIGHTER)
            fighter_b_id = self._insert_user(session, "fighter.security.b@example.test", UserRole.FIGHTER)
            service = BoutService(session=session)
            bout = service.create_bout_draft(
                promoter_user_id=promoter_id,
                fighter_a_user_id=fighter_a_id,
                fighter_b_user_id=fighter_b_id,
                event_datetime_utc=datetime(2026, 2, 18, 18, 0, 0, tzinfo=UTC),
                promoter_owner_address="rPromoterSecurity",
                fighter_a_destination="rFighterSecurityA",
                fighter_b_destination="rFighterSecurityB",
                show_a_drops=1_000_000,
                show_b_drops=1_000_000,
                bonus_a_drops=100_000,
                bonus_b_drops=100_000,
            )
            session.commit()
            return bout.id, promoter_id, promoter_email

    @staticmethod
    def _insert_user(session: Session, email: str, role: UserRole) -> uuid.UUID:
        user = User(id=uuid.uuid4(), email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
        session.add(user)
        session.flush()
        return user.id

    def _confirm_payload(self) -> dict[str, object]:
        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_A)
            )
            assert escrow is not None
            return {
                "escrow_kind": EscrowKind.SHOW_A.value,
                "tx_hash": "TXSECURITY001",
                "offer_sequence": 8001,
                "validated": True,
                "engine_result": "tesSUCCESS",
                "owner_address": escrow.owner_address,
                "destination_address": escrow.destination_address,
                "amount_drops": escrow.amount_drops,
                "finish_after_ripple": escrow.finish_after_ripple,
                "cancel_after_ripple": escrow.cancel_after_ripple,
                "condition_hex": escrow.condition_hex,
            }

    def _promoter_headers(self) -> dict[str, str]:
        token = create_access_token(
            subject=str(self.promoter_user_id),
            email=self.promoter_email,
            role=UserRole.PROMOTER.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    unittest.main()
