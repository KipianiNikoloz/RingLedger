from __future__ import annotations

import unittest
import uuid
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_session
from app.integrations.xaman_service import XamanIntegrationError
from app.main import create_app
from app.models.audit_log import AuditLog
from app.models.bout import Bout
from app.models.enums import EscrowKind, EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.idempotency_key import IdempotencyKey
from app.models.user import User
from app.services.bout_service import BoutService


class EscrowConfirmIntegrationTests(unittest.TestCase):
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

    def test_prepare_returns_unsigned_escrow_create_payloads(self) -> None:
        response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/prepare",
            headers=self._promoter_headers(),
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["bout_id"], str(self.bout_id))
        self.assertEqual(len(body["escrows"]), 4)
        for item in body["escrows"]:
            sign_request = item.get("xaman_sign_request")
            self.assertIsInstance(sign_request, dict)
            self.assertIn("payload_id", sign_request)
            self.assertTrue(sign_request["deep_link_url"].startswith("xumm://payload/"))
            self.assertTrue(sign_request["qr_png_url"].startswith("https://xumm.app/sign/"))
            self.assertEqual(sign_request["mode"], "stub")

        payloads = {item["escrow_kind"]: item["unsigned_tx"] for item in body["escrows"]}
        self.assertEqual(
            set(payloads),
            {EscrowKind.SHOW_A.value, EscrowKind.SHOW_B.value, EscrowKind.BONUS_A.value, EscrowKind.BONUS_B.value},
        )
        for tx in payloads.values():
            self.assertEqual(tx["TransactionType"], "EscrowCreate")
            self.assertIn("Account", tx)
            self.assertIn("Destination", tx)
            self.assertIn("Amount", tx)
            self.assertIn("FinishAfter", tx)

        self.assertNotIn("CancelAfter", payloads[EscrowKind.SHOW_A.value])
        self.assertNotIn("CancelAfter", payloads[EscrowKind.SHOW_B.value])
        self.assertIn("CancelAfter", payloads[EscrowKind.BONUS_A.value])
        self.assertIn("CancelAfter", payloads[EscrowKind.BONUS_B.value])

    def test_prepare_returns_502_when_xaman_sign_request_fails(self) -> None:
        xaman_mock = Mock()
        xaman_mock.create_sign_request.side_effect = XamanIntegrationError("xaman_api_connection_error")
        with patch("app.api.bouts.XamanService.from_settings", return_value=xaman_mock):
            response = self.client.post(
                f"/bouts/{self.bout_id}/escrows/prepare",
                headers=self._promoter_headers(),
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "Xaman signing request could not be prepared.")

    def test_confirm_transitions_all_escrows_and_marks_bout_escrows_created(self) -> None:
        confirmations = [
            (EscrowKind.SHOW_A, "TX00000001", 1001),
            (EscrowKind.SHOW_B, "TX00000002", 1002),
            (EscrowKind.BONUS_A, "TX00000003", 1003),
            (EscrowKind.BONUS_B, "TX00000004", 1004),
        ]

        for index, (kind, tx_hash, offer_sequence) in enumerate(confirmations):
            payload = self._build_confirm_payload(kind=kind, tx_hash=tx_hash, offer_sequence=offer_sequence)
            response = self.client.post(
                f"/bouts/{self.bout_id}/escrows/confirm",
                headers=self._promoter_headers({"Idempotency-Key": f"confirm-{kind.value}"}),
                json=payload,
            )
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(body["escrow_kind"], kind.value)
            self.assertEqual(body["escrow_status"], EscrowStatus.CREATED.value)
            expected_bout_status = "escrows_created" if index == len(confirmations) - 1 else "draft"
            self.assertEqual(body["bout_status"], expected_bout_status)
            self.assertEqual(body["tx_hash"], tx_hash)
            self.assertEqual(body["offer_sequence"], offer_sequence)

        with Session(self.engine) as session:
            bout = session.get(Bout, self.bout_id)
            assert bout is not None
            self.assertEqual(bout.status.value, "escrows_created")
            escrows = session.scalars(select(Escrow).where(Escrow.bout_id == self.bout_id)).all()
            self.assertEqual(len(escrows), 4)
            self.assertTrue(all(item.status == EscrowStatus.CREATED for item in escrows))
            self.assertTrue(all(item.create_tx_hash is not None for item in escrows))
            self.assertTrue(all(item.offer_sequence is not None for item in escrows))

    def test_confirm_supports_idempotent_replay_and_payload_collision_rejection(self) -> None:
        payload = self._build_confirm_payload(
            kind=EscrowKind.SHOW_A,
            tx_hash="TX00000011",
            offer_sequence=1111,
        )
        response_one = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers({"Idempotency-Key": "replay-key"}),
            json=payload,
        )
        self.assertEqual(response_one.status_code, 200)

        response_two = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers({"Idempotency-Key": "replay-key"}),
            json=payload,
        )
        self.assertEqual(response_two.status_code, 200)
        self.assertEqual(response_two.json(), response_one.json())

        payload_collision = dict(payload)
        payload_collision["tx_hash"] = "TX00000999"
        response_three = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers({"Idempotency-Key": "replay-key"}),
            json=payload_collision,
        )
        self.assertEqual(response_three.status_code, 409)
        self.assertIn("different request payload", response_three.json()["detail"])

        with Session(self.engine) as session:
            scope = f"escrow_create_confirm:{self.bout_id}"
            stored_count = session.scalar(
                select(func.count())
                .select_from(IdempotencyKey)
                .where(
                    IdempotencyKey.scope == scope,
                    IdempotencyKey.idempotency_key == "replay-key",
                )
            )
            self.assertEqual(stored_count, 1)

    def test_confirm_rejects_invalid_confirmation_and_records_audit(self) -> None:
        payload = self._build_confirm_payload(
            kind=EscrowKind.SHOW_B,
            tx_hash="TX00000021",
            offer_sequence=2221,
            validated=False,
        )
        response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers({"Idempotency-Key": "invalid-confirm"}),
            json=payload,
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Ledger confirmation failed validation.")

        replay = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._promoter_headers({"Idempotency-Key": "invalid-confirm"}),
            json=payload,
        )
        self.assertEqual(replay.status_code, 422)
        self.assertEqual(replay.json(), response.json())

        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_B)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.PLANNED)
            self.assertEqual(escrow.failure_code, "invalid_confirmation")

            audit = session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "escrow_create_confirm",
                    AuditLog.entity_id == str(escrow.id),
                    AuditLog.outcome == "rejected",
                )
            )
            self.assertIsNotNone(audit)

    def _override_get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def _seed_bout(self) -> tuple[uuid.UUID, uuid.UUID, str]:
        with Session(self.engine) as session:
            promoter_email = "promoter.m2@example.test"
            promoter_id = self._insert_user(session, promoter_email, UserRole.PROMOTER)
            fighter_a_id = self._insert_user(session, "fighter.m2.a@example.test", UserRole.FIGHTER)
            fighter_b_id = self._insert_user(session, "fighter.m2.b@example.test", UserRole.FIGHTER)
            service = BoutService(session=session)
            bout = service.create_bout_draft(
                promoter_user_id=promoter_id,
                fighter_a_user_id=fighter_a_id,
                fighter_b_user_id=fighter_b_id,
                event_datetime_utc=self._event_datetime(),
                promoter_owner_address="rPromoterM2",
                fighter_a_destination="rFighterM2A",
                fighter_b_destination="rFighterM2B",
                show_a_drops=1_000_000,
                show_b_drops=1_500_000,
                bonus_a_drops=250_000,
                bonus_b_drops=250_000,
            )
            session.commit()
            return bout.id, promoter_id, promoter_email

    @staticmethod
    def _event_datetime():
        from datetime import UTC, datetime

        return datetime(2026, 2, 18, 20, 0, 0, tzinfo=UTC)

    @staticmethod
    def _insert_user(session: Session, email: str, role: UserRole) -> uuid.UUID:
        user = User(id=uuid.uuid4(), email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
        session.add(user)
        session.flush()
        return user.id

    def _build_confirm_payload(
        self,
        *,
        kind: EscrowKind,
        tx_hash: str,
        offer_sequence: int,
        validated: bool = True,
        engine_result: str = "tesSUCCESS",
    ) -> dict[str, object]:
        with Session(self.engine) as session:
            escrow = session.scalar(select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == kind))
            assert escrow is not None
            return {
                "escrow_kind": kind.value,
                "tx_hash": tx_hash,
                "offer_sequence": offer_sequence,
                "validated": validated,
                "engine_result": engine_result,
                "owner_address": escrow.owner_address,
                "destination_address": escrow.destination_address,
                "amount_drops": escrow.amount_drops,
                "finish_after_ripple": escrow.finish_after_ripple,
                "cancel_after_ripple": escrow.cancel_after_ripple,
                "condition_hex": escrow.condition_hex,
            }

    def _promoter_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        token = create_access_token(
            subject=str(self.promoter_user_id),
            email=self.promoter_email,
            role=UserRole.PROMOTER.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        headers = {"Authorization": f"Bearer {token}"}
        if extra:
            headers.update(extra)
        return headers


if __name__ == "__main__":
    unittest.main()
