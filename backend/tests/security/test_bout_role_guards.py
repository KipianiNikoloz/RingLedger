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


class BoutRoleGuardsSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        self.bout_id, self.promoter_user_id, self.promoter_email, self.admin_user_id, self.admin_email = (
            self._seed_bout()
        )

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

    def test_bout_routes_require_authorization_header(self) -> None:
        response = self.client.post(f"/bouts/{self.bout_id}/escrows/prepare")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Authorization header is required.")

    def test_result_route_rejects_non_admin_actor(self) -> None:
        response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            json={"winner": "A"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Insufficient role for this operation.")

    def test_payout_confirm_still_requires_idempotency_key(self) -> None:
        payload = self._payout_confirm_payload(escrow_kind=EscrowKind.SHOW_A)
        response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            json=payload,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Idempotency-Key header is required.")

    def _seed_bout(self) -> tuple[uuid.UUID, uuid.UUID, str, uuid.UUID, str]:
        with Session(self.engine) as session:
            promoter_email = "promoter.security.roles@example.test"
            admin_email = "admin.security.roles@example.test"
            promoter_id = self._insert_user(session, promoter_email, UserRole.PROMOTER)
            admin_id = self._insert_user(session, admin_email, UserRole.ADMIN)
            fighter_a_id = self._insert_user(session, "fighter.roles.a@example.test", UserRole.FIGHTER)
            fighter_b_id = self._insert_user(session, "fighter.roles.b@example.test", UserRole.FIGHTER)

            bout = BoutService(session=session).create_bout_draft(
                promoter_user_id=promoter_id,
                fighter_a_user_id=fighter_a_id,
                fighter_b_user_id=fighter_b_id,
                event_datetime_utc=datetime(2026, 2, 18, 18, 0, 0, tzinfo=UTC),
                promoter_owner_address="rPromoterRoles",
                fighter_a_destination="rFighterRolesA",
                fighter_b_destination="rFighterRolesB",
                show_a_drops=1_000_000,
                show_b_drops=1_000_000,
                bonus_a_drops=200_000,
                bonus_b_drops=200_000,
            )
            session.commit()
            return bout.id, promoter_id, promoter_email, admin_id, admin_email

    def _payout_confirm_payload(self, *, escrow_kind: EscrowKind) -> dict[str, object]:
        with Session(self.engine) as session:
            escrow = session.scalar(select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == escrow_kind))
            assert escrow is not None
            offer_sequence = escrow.offer_sequence or 9001
            return {
                "escrow_kind": escrow_kind.value,
                "tx_hash": "TXROLE0001",
                "validated": True,
                "engine_result": "tesSUCCESS",
                "transaction_type": "EscrowFinish",
                "owner_address": escrow.owner_address,
                "offer_sequence": offer_sequence,
                "close_time_ripple": escrow.finish_after_ripple,
                "fulfillment_hex": None,
            }

    def _override_get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def _insert_user(session: Session, email: str, role: UserRole) -> uuid.UUID:
        user = User(id=uuid.uuid4(), email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
        session.add(user)
        session.flush()
        return user.id

    def _auth_headers(self, user_id: uuid.UUID, email: str, role: UserRole) -> dict[str, str]:
        token = create_access_token(
            subject=str(user_id),
            email=email,
            role=role.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    unittest.main()
