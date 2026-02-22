from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
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
from app.models.enums import BoutStatus, EscrowKind, EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.user import User
from app.services.bout_service import BoutService


class PayoutFlowIntegrationTests(unittest.TestCase):
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
            self._seed_bout_with_created_escrows()
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

    def test_admin_result_and_promoter_payout_confirm_flow_closes_bout(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)
        self.assertEqual(result_response.json()["bout_status"], BoutStatus.RESULT_ENTERED.value)
        self.assertEqual(result_response.json()["winner"], "A")

        prepare_response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/prepare",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
        )
        self.assertEqual(prepare_response.status_code, 200)
        prepare_body = prepare_response.json()
        for item in prepare_body["escrows"]:
            sign_request = item.get("xaman_sign_request")
            self.assertIsInstance(sign_request, dict)
            self.assertIn("payload_id", sign_request)
            self.assertTrue(sign_request["deep_link_url"].startswith("xumm://payload/"))
            self.assertTrue(sign_request["qr_png_url"].startswith("https://xumm.app/sign/"))
            self.assertEqual(sign_request["mode"], "stub")
        actions = {item["escrow_kind"]: item["action"] for item in prepare_body["escrows"]}
        self.assertEqual(
            actions,
            {
                EscrowKind.SHOW_A.value: "finish",
                EscrowKind.SHOW_B.value: "finish",
                EscrowKind.BONUS_A.value: "finish",
                EscrowKind.BONUS_B.value: "cancel",
            },
        )

        show_a_payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.SHOW_A,
            tx_hash="TXPAYOUT0001",
            transaction_type="EscrowFinish",
        )
        show_a_confirm = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-show-a"},
            ),
            json=show_a_payload,
        )
        self.assertEqual(show_a_confirm.status_code, 200)
        self.assertEqual(show_a_confirm.json()["bout_status"], BoutStatus.PAYOUTS_IN_PROGRESS.value)

        show_b_payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.SHOW_B,
            tx_hash="TXPAYOUT0002",
            transaction_type="EscrowFinish",
        )
        show_b_confirm = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-show-b"},
            ),
            json=show_b_payload,
        )
        self.assertEqual(show_b_confirm.status_code, 200)
        self.assertEqual(show_b_confirm.json()["bout_status"], BoutStatus.PAYOUTS_IN_PROGRESS.value)

        winner_bonus_payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.BONUS_A,
            tx_hash="TXPAYOUT0003",
            transaction_type="EscrowFinish",
        )
        winner_bonus_confirm = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-bonus-a"},
            ),
            json=winner_bonus_payload,
        )
        self.assertEqual(winner_bonus_confirm.status_code, 200)
        self.assertEqual(winner_bonus_confirm.json()["escrow_status"], EscrowStatus.FINISHED.value)
        self.assertEqual(winner_bonus_confirm.json()["bout_status"], BoutStatus.CLOSED.value)

        with Session(self.engine) as session:
            bout = session.get(Bout, self.bout_id)
            assert bout is not None
            self.assertEqual(bout.status, BoutStatus.CLOSED)
            escrows = session.scalars(select(Escrow).where(Escrow.bout_id == self.bout_id)).all()
            status_by_kind = {item.kind: item.status for item in escrows}
            self.assertEqual(status_by_kind[EscrowKind.SHOW_A], EscrowStatus.FINISHED)
            self.assertEqual(status_by_kind[EscrowKind.SHOW_B], EscrowStatus.FINISHED)
            self.assertEqual(status_by_kind[EscrowKind.BONUS_A], EscrowStatus.FINISHED)

    def test_payout_prepare_returns_502_when_xaman_sign_request_fails(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)

        xaman_mock = Mock()
        xaman_mock.create_sign_request.side_effect = XamanIntegrationError("xaman_api_connection_error")
        with patch("app.api.bouts.XamanService.from_settings", return_value=xaman_mock):
            response = self.client.post(
                f"/bouts/{self.bout_id}/payouts/prepare",
                headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "Xaman signing request could not be prepared.")

    def test_payout_signing_reconcile_declined_sets_failure_without_transition(self) -> None:
        self._enter_result(winner="A")
        payload_id = self._prepare_payout_payload_id(EscrowKind.SHOW_A)
        response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/signing/reconcile",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            json={
                "escrow_kind": EscrowKind.SHOW_A.value,
                "payload_id": payload_id,
                "observed_status": "declined",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["signing_status"], "declined")
        self.assertEqual(response.json()["failure_code"], "signing_declined")
        self.assertEqual(response.json()["escrow_status"], EscrowStatus.CREATED.value)

        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_A)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.CREATED)
            self.assertEqual(escrow.failure_code, "signing_declined")

    def test_payout_signing_reconcile_signed_clears_signing_failure_without_transition(self) -> None:
        self._enter_result(winner="A")
        payload_id = self._prepare_payout_payload_id(EscrowKind.SHOW_B)
        first = self.client.post(
            f"/bouts/{self.bout_id}/payouts/signing/reconcile",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            json={
                "escrow_kind": EscrowKind.SHOW_B.value,
                "payload_id": payload_id,
                "observed_status": "expired",
            },
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["failure_code"], "signing_expired")

        second = self.client.post(
            f"/bouts/{self.bout_id}/payouts/signing/reconcile",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
            json={
                "escrow_kind": EscrowKind.SHOW_B.value,
                "payload_id": payload_id,
                "observed_status": "signed",
                "observed_tx_hash": "HASHSIGNED",
            },
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["signing_status"], "signed")
        self.assertIsNone(second.json()["failure_code"])
        self.assertEqual(second.json()["tx_hash"], "HASHSIGNED")

        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_B)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.CREATED)
            self.assertIsNone(escrow.failure_code)

    def test_loser_bonus_cancel_before_cancel_after_is_rejected(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)

        loser_bonus_payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.BONUS_B,
            tx_hash="TXPAYOUT0099",
            transaction_type="EscrowCancel",
            close_time_offset=-1,
        )
        confirm_response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-bonus-b-too-early"},
            ),
            json=loser_bonus_payload,
        )
        self.assertEqual(confirm_response.status_code, 422)
        self.assertEqual(confirm_response.json()["detail"], "Ledger confirmation failed validation.")

    def test_payout_confirm_rejects_declined_signing_with_failure_classification(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)

        payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.SHOW_A,
            tx_hash="TXPAYOUTDECLINE1",
            transaction_type="EscrowFinish",
            validated=False,
            engine_result="declined",
        )
        response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-declined"},
            ),
            json=payload,
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Signing was declined; no state transition was applied.")

        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_A)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.CREATED)
            self.assertEqual(escrow.failure_code, "signing_declined")

    def test_payout_confirm_rejects_tec_tem_with_failure_classification(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)

        payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.SHOW_B,
            tx_hash="TXPAYOUTTEC1",
            transaction_type="EscrowFinish",
            validated=True,
            engine_result="temMALFORMED",
        )
        response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-tec-tem"},
            ),
            json=payload,
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"],
            "Ledger transaction was rejected with tec/tem; no state transition was applied.",
        )

        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_B)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.CREATED)
            self.assertEqual(escrow.failure_code, "ledger_tec_tem")
            audit = session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "escrow_payout_confirm",
                    AuditLog.entity_id == str(escrow.id),
                    AuditLog.outcome == "rejected",
                )
            )
            self.assertIsNotNone(audit)

    def test_payout_confirm_supports_idempotent_replay_and_payload_collision_rejection(self) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)

        payload = self._build_confirm_payload(
            escrow_kind=EscrowKind.SHOW_A,
            tx_hash="TXPAYOUTREPLAY1",
            transaction_type="EscrowFinish",
        )
        first = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-replay"},
            ),
            json=payload,
        )
        self.assertEqual(first.status_code, 200)

        replay = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-replay"},
            ),
            json=payload,
        )
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json(), first.json())

        collision = dict(payload)
        collision["tx_hash"] = "TXPAYOUTREPLAY2"
        mismatch = self.client.post(
            f"/bouts/{self.bout_id}/payouts/confirm",
            headers=self._auth_headers(
                self.promoter_user_id,
                self.promoter_email,
                UserRole.PROMOTER,
                extra={"Idempotency-Key": "payout-replay"},
            ),
            json=collision,
        )
        self.assertEqual(mismatch.status_code, 409)
        self.assertIn("different request payload", mismatch.json()["detail"])

    def _seed_bout_with_created_escrows(self) -> tuple[uuid.UUID, uuid.UUID, str, uuid.UUID, str]:
        with Session(self.engine) as session:
            promoter_email = "promoter.payout@example.test"
            admin_email = "admin.payout@example.test"
            promoter_id = self._insert_user(session, promoter_email, UserRole.PROMOTER)
            admin_id = self._insert_user(session, admin_email, UserRole.ADMIN)
            fighter_a_id = self._insert_user(session, "fighter.payout.a@example.test", UserRole.FIGHTER)
            fighter_b_id = self._insert_user(session, "fighter.payout.b@example.test", UserRole.FIGHTER)

            service = BoutService(session=session)
            bout = service.create_bout_draft(
                promoter_user_id=promoter_id,
                fighter_a_user_id=fighter_a_id,
                fighter_b_user_id=fighter_b_id,
                event_datetime_utc=datetime(2026, 2, 18, 20, 0, 0, tzinfo=UTC),
                promoter_owner_address="rPromoterPayout",
                fighter_a_destination="rFighterPayoutA",
                fighter_b_destination="rFighterPayoutB",
                show_a_drops=1_000_000,
                show_b_drops=1_100_000,
                bonus_a_drops=250_000,
                bonus_b_drops=250_000,
            )

            escrows = session.scalars(select(Escrow).where(Escrow.bout_id == bout.id)).all()
            for index, escrow in enumerate(escrows, start=1):
                escrow.status = EscrowStatus.CREATED
                escrow.offer_sequence = 6000 + index
                escrow.create_tx_hash = f"TXCREATE{index:04d}"
            bout.status = BoutStatus.ESCROWS_CREATED
            session.commit()
            return bout.id, promoter_id, promoter_email, admin_id, admin_email

    def _enter_result(self, *, winner: str) -> None:
        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_user_id, self.admin_email, UserRole.ADMIN),
            json={"winner": winner},
        )
        self.assertEqual(result_response.status_code, 200)

    def _prepare_payout_payload_id(self, escrow_kind: EscrowKind) -> str:
        prepare_response = self.client.post(
            f"/bouts/{self.bout_id}/payouts/prepare",
            headers=self._auth_headers(self.promoter_user_id, self.promoter_email, UserRole.PROMOTER),
        )
        self.assertEqual(prepare_response.status_code, 200)
        item = next(item for item in prepare_response.json()["escrows"] if item["escrow_kind"] == escrow_kind.value)
        return item["xaman_sign_request"]["payload_id"]

    def _build_confirm_payload(
        self,
        *,
        escrow_kind: EscrowKind,
        tx_hash: str,
        transaction_type: str,
        close_time_offset: int = 0,
        validated: bool = True,
        engine_result: str = "tesSUCCESS",
    ) -> dict[str, object]:
        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(
                    Escrow.bout_id == self.bout_id,
                    Escrow.kind == escrow_kind,
                )
            )
            assert escrow is not None
            if transaction_type == "EscrowCancel":
                assert escrow.cancel_after_ripple is not None
                close_time_ripple = escrow.cancel_after_ripple + close_time_offset
            else:
                close_time_ripple = escrow.finish_after_ripple + close_time_offset
            return {
                "escrow_kind": escrow.kind.value,
                "tx_hash": tx_hash,
                "validated": validated,
                "engine_result": engine_result,
                "transaction_type": transaction_type,
                "owner_address": escrow.owner_address,
                "offer_sequence": escrow.offer_sequence,
                "close_time_ripple": close_time_ripple,
                "fulfillment_hex": escrow.encrypted_preimage_hex if escrow.kind == EscrowKind.BONUS_A else None,
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

    def _auth_headers(
        self,
        user_id: uuid.UUID,
        email: str,
        role: UserRole,
        *,
        extra: dict[str, str] | None = None,
    ) -> dict[str, str]:
        token = create_access_token(
            subject=str(user_id),
            email=email,
            role=role.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        headers = {"Authorization": f"Bearer {token}"}
        if extra:
            headers.update(extra)
        return headers


if __name__ == "__main__":
    unittest.main()
