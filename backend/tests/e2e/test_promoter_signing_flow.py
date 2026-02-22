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
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.bout import Bout
from app.models.enums import BoutStatus, EscrowKind, EscrowStatus
from app.models.escrow import Escrow
from app.models.user import User
from app.services.bout_service import BoutService


class PromoterSigningFlowE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

        self.init_db_patcher = patch("app.main.init_db")
        self.init_db_patcher.start()
        self.app = create_app()
        self.app.dependency_overrides[get_session] = self._override_get_session
        self.client = TestClient(self.app)
        self.client.__enter__()

        self.promoter_email = "promoter.e2e@example.com"
        self.promoter_password = "PromoterPass123!"
        self.admin_email = "admin.e2e@example.com"
        self.admin_password = "AdminPass123!"
        self.fighter_a_email = "fighter.e2e.a@example.com"
        self.fighter_a_password = "FighterPassA123!"
        self.fighter_b_email = "fighter.e2e.b@example.com"
        self.fighter_b_password = "FighterPassB123!"

        self.promoter_user_id, self.promoter_token = self._register_and_login(
            email=self.promoter_email,
            password=self.promoter_password,
            role="promoter",
        )
        self.admin_user_id, self.admin_token = self._register_and_login(
            email=self.admin_email,
            password=self.admin_password,
            role="admin",
        )
        self.fighter_a_user_id, _ = self._register_and_login(
            email=self.fighter_a_email,
            password=self.fighter_a_password,
            role="fighter",
        )
        self.fighter_b_user_id, _ = self._register_and_login(
            email=self.fighter_b_email,
            password=self.fighter_b_password,
            role="fighter",
        )
        self.bout_id = self._create_bout_draft()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        self.init_db_patcher.stop()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_frontend_happy_path_contract_from_login_to_closeout(self) -> None:
        escrow_prepare = self.client.post(
            f"/bouts/{self.bout_id}/escrows/prepare",
            headers=self._auth_headers(self.promoter_token),
        )
        self.assertEqual(escrow_prepare.status_code, 200)
        escrow_prepare_body = escrow_prepare.json()
        self.assertEqual(escrow_prepare_body["bout_id"], str(self.bout_id))
        self.assertEqual(len(escrow_prepare_body["escrows"]), 4)

        escrow_items_by_kind = {item["escrow_kind"]: item for item in escrow_prepare_body["escrows"]}
        for kind in EscrowKind:
            self.assertIn(kind.value, escrow_items_by_kind)
            escrow_item = escrow_items_by_kind[kind.value]
            self.assertIn("escrow_id", escrow_item)
            self.assertIn("unsigned_tx", escrow_item)
            self.assertIn("xaman_sign_request", escrow_item)
            self._assert_sign_request_shape(escrow_item["xaman_sign_request"])

        reconcile_open = self.client.post(
            f"/bouts/{self.bout_id}/escrows/signing/reconcile",
            headers=self._auth_headers(self.promoter_token),
            json={
                "escrow_kind": EscrowKind.SHOW_A.value,
                "payload_id": escrow_items_by_kind[EscrowKind.SHOW_A.value]["xaman_sign_request"]["payload_id"],
                "observed_status": "open",
            },
        )
        self.assertEqual(reconcile_open.status_code, 200)
        self.assertEqual(reconcile_open.json()["signing_status"], "open")
        self.assertIsNone(reconcile_open.json()["failure_code"])
        self.assertEqual(reconcile_open.json()["escrow_status"], EscrowStatus.PLANNED.value)

        escrow_confirm_cases = [
            (EscrowKind.SHOW_A, "TXE2ECREATE0001", 9001),
            (EscrowKind.SHOW_B, "TXE2ECREATE0002", 9002),
            (EscrowKind.BONUS_A, "TXE2ECREATE0003", 9003),
            (EscrowKind.BONUS_B, "TXE2ECREATE0004", 9004),
        ]
        for kind, tx_hash, offer_sequence in escrow_confirm_cases:
            confirm_response = self.client.post(
                f"/bouts/{self.bout_id}/escrows/confirm",
                headers=self._auth_headers(
                    self.promoter_token,
                    extra={"Idempotency-Key": f"e2e-escrow-{kind.value}"},
                ),
                json=self._build_escrow_confirm_payload(
                    escrow_kind=kind,
                    tx_hash=tx_hash,
                    offer_sequence=offer_sequence,
                ),
            )
            self.assertEqual(confirm_response.status_code, 200)
            confirm_body = confirm_response.json()
            self.assertEqual(confirm_body["escrow_kind"], kind.value)
            self.assertEqual(confirm_body["escrow_status"], EscrowStatus.CREATED.value)
            self.assertIn("bout_status", confirm_body)
            self.assertEqual(confirm_body["tx_hash"], tx_hash)
            self.assertEqual(confirm_body["offer_sequence"], offer_sequence)

        with Session(self.engine) as session:
            bout_after_escrows = session.get(Bout, self.bout_id)
            assert bout_after_escrows is not None
            self.assertEqual(bout_after_escrows.status, BoutStatus.ESCROWS_CREATED)

        result_response = self.client.post(
            f"/bouts/{self.bout_id}/result",
            headers=self._auth_headers(self.admin_token),
            json={"winner": "A"},
        )
        self.assertEqual(result_response.status_code, 200)
        self.assertEqual(result_response.json()["bout_status"], BoutStatus.RESULT_ENTERED.value)
        self.assertEqual(result_response.json()["winner"], "A")

        payout_prepare = self.client.post(
            f"/bouts/{self.bout_id}/payouts/prepare",
            headers=self._auth_headers(self.promoter_token),
        )
        self.assertEqual(payout_prepare.status_code, 200)
        payout_prepare_body = payout_prepare.json()
        self.assertEqual(payout_prepare_body["bout_status"], BoutStatus.RESULT_ENTERED.value)
        self.assertEqual(len(payout_prepare_body["escrows"]), 4)

        payout_items_by_kind = {item["escrow_kind"]: item for item in payout_prepare_body["escrows"]}
        expected_actions = {
            EscrowKind.SHOW_A.value: "finish",
            EscrowKind.SHOW_B.value: "finish",
            EscrowKind.BONUS_A.value: "finish",
            EscrowKind.BONUS_B.value: "cancel",
        }
        actual_actions = {kind: item["action"] for kind, item in payout_items_by_kind.items()}
        self.assertEqual(actual_actions, expected_actions)
        for item in payout_prepare_body["escrows"]:
            self.assertIn("xaman_sign_request", item)
            self._assert_sign_request_shape(item["xaman_sign_request"])

        reconcile_expired = self.client.post(
            f"/bouts/{self.bout_id}/payouts/signing/reconcile",
            headers=self._auth_headers(self.promoter_token),
            json={
                "escrow_kind": EscrowKind.SHOW_B.value,
                "payload_id": payout_items_by_kind[EscrowKind.SHOW_B.value]["xaman_sign_request"]["payload_id"],
                "observed_status": "expired",
            },
        )
        self.assertEqual(reconcile_expired.status_code, 200)
        self.assertEqual(reconcile_expired.json()["signing_status"], "expired")
        self.assertEqual(reconcile_expired.json()["failure_code"], "signing_expired")
        self.assertEqual(reconcile_expired.json()["escrow_status"], EscrowStatus.CREATED.value)

        reconcile_signed = self.client.post(
            f"/bouts/{self.bout_id}/payouts/signing/reconcile",
            headers=self._auth_headers(self.promoter_token),
            json={
                "escrow_kind": EscrowKind.SHOW_B.value,
                "payload_id": payout_items_by_kind[EscrowKind.SHOW_B.value]["xaman_sign_request"]["payload_id"],
                "observed_status": "signed",
                "observed_tx_hash": "TXSIGNEDE2E01",
            },
        )
        self.assertEqual(reconcile_signed.status_code, 200)
        self.assertEqual(reconcile_signed.json()["signing_status"], "signed")
        self.assertIsNone(reconcile_signed.json()["failure_code"])
        self.assertEqual(reconcile_signed.json()["tx_hash"], "TXSIGNEDE2E01")

        payout_confirm_cases = [
            (EscrowKind.SHOW_A, "TXE2EPAYOUT0001"),
            (EscrowKind.SHOW_B, "TXE2EPAYOUT0002"),
            (EscrowKind.BONUS_A, "TXE2EPAYOUT0003"),
        ]
        last_bout_status = ""
        for kind, tx_hash in payout_confirm_cases:
            payout_confirm_response = self.client.post(
                f"/bouts/{self.bout_id}/payouts/confirm",
                headers=self._auth_headers(
                    self.promoter_token,
                    extra={"Idempotency-Key": f"e2e-payout-{kind.value}"},
                ),
                json=self._build_payout_confirm_payload(
                    escrow_kind=kind,
                    tx_hash=tx_hash,
                    transaction_type="EscrowFinish",
                ),
            )
            self.assertEqual(payout_confirm_response.status_code, 200)
            payout_confirm_body = payout_confirm_response.json()
            self.assertEqual(payout_confirm_body["escrow_kind"], kind.value)
            self.assertEqual(payout_confirm_body["escrow_status"], EscrowStatus.FINISHED.value)
            self.assertEqual(payout_confirm_body["tx_hash"], tx_hash)
            self.assertIn("bout_status", payout_confirm_body)
            last_bout_status = payout_confirm_body["bout_status"]

        self.assertEqual(last_bout_status, BoutStatus.CLOSED.value)
        with Session(self.engine) as session:
            bout = session.get(Bout, self.bout_id)
            assert bout is not None
            self.assertEqual(bout.status, BoutStatus.CLOSED)
            escrows = session.scalars(select(Escrow).where(Escrow.bout_id == self.bout_id)).all()
            status_by_kind = {escrow.kind: escrow.status for escrow in escrows}
            self.assertEqual(status_by_kind[EscrowKind.SHOW_A], EscrowStatus.FINISHED)
            self.assertEqual(status_by_kind[EscrowKind.SHOW_B], EscrowStatus.FINISHED)
            self.assertEqual(status_by_kind[EscrowKind.BONUS_A], EscrowStatus.FINISHED)
            self.assertEqual(status_by_kind[EscrowKind.BONUS_B], EscrowStatus.CREATED)

    def test_frontend_declined_signing_failure_is_actionable_and_replay_safe(self) -> None:
        prepare_response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/prepare",
            headers=self._auth_headers(self.promoter_token),
        )
        self.assertEqual(prepare_response.status_code, 200)
        escrow_items_by_kind = {item["escrow_kind"]: item for item in prepare_response.json()["escrows"]}
        payload_id = escrow_items_by_kind[EscrowKind.SHOW_B.value]["xaman_sign_request"]["payload_id"]

        reconcile_declined = self.client.post(
            f"/bouts/{self.bout_id}/escrows/signing/reconcile",
            headers=self._auth_headers(self.promoter_token),
            json={
                "escrow_kind": EscrowKind.SHOW_B.value,
                "payload_id": payload_id,
                "observed_status": "declined",
            },
        )
        self.assertEqual(reconcile_declined.status_code, 200)
        self.assertEqual(reconcile_declined.json()["signing_status"], "declined")
        self.assertEqual(reconcile_declined.json()["failure_code"], "signing_declined")
        self.assertEqual(reconcile_declined.json()["escrow_status"], EscrowStatus.PLANNED.value)

        declined_confirmation_payload = self._build_escrow_confirm_payload(
            escrow_kind=EscrowKind.SHOW_B,
            tx_hash="TXE2EDECLINED001",
            offer_sequence=9702,
            validated=False,
            engine_result="declined",
        )
        declined_response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._auth_headers(self.promoter_token, extra={"Idempotency-Key": "e2e-declined-signing"}),
            json=declined_confirmation_payload,
        )
        self.assertEqual(declined_response.status_code, 422)
        self.assertEqual(declined_response.json()["detail"], "Signing was declined; no state transition was applied.")

        replay_response = self.client.post(
            f"/bouts/{self.bout_id}/escrows/confirm",
            headers=self._auth_headers(self.promoter_token, extra={"Idempotency-Key": "e2e-declined-signing"}),
            json=declined_confirmation_payload,
        )
        self.assertEqual(replay_response.status_code, 422)
        self.assertEqual(replay_response.json(), declined_response.json())

        with Session(self.engine) as session:
            bout = session.get(Bout, self.bout_id)
            assert bout is not None
            self.assertEqual(bout.status, BoutStatus.DRAFT)

            escrow = session.scalar(
                select(Escrow).where(Escrow.bout_id == self.bout_id, Escrow.kind == EscrowKind.SHOW_B)
            )
            assert escrow is not None
            self.assertEqual(escrow.status, EscrowStatus.PLANNED)
            self.assertEqual(escrow.failure_code, "signing_declined")

    def _register_and_login(self, *, email: str, password: str, role: str) -> tuple[uuid.UUID, str]:
        register_response = self.client.post(
            "/auth/register",
            json={"email": email, "password": password, "role": role},
        )
        self.assertEqual(register_response.status_code, 201)
        register_body = register_response.json()
        self.assertEqual(register_body["email"], email)
        self.assertEqual(register_body["role"], role)
        user_id = uuid.UUID(register_body["user_id"])

        login_response = self.client.post("/auth/login", json={"email": email, "password": password})
        self.assertEqual(login_response.status_code, 200)
        login_body = login_response.json()
        self.assertIn("access_token", login_body)
        self.assertEqual(login_body["token_type"], "bearer")
        return user_id, login_body["access_token"]

    def _create_bout_draft(self) -> uuid.UUID:
        with Session(self.engine) as session:
            for user_id in [
                self.promoter_user_id,
                self.fighter_a_user_id,
                self.fighter_b_user_id,
                self.admin_user_id,
            ]:
                user = session.get(User, user_id)
                self.assertIsNotNone(user)

            service = BoutService(session=session)
            bout = service.create_bout_draft(
                promoter_user_id=self.promoter_user_id,
                fighter_a_user_id=self.fighter_a_user_id,
                fighter_b_user_id=self.fighter_b_user_id,
                event_datetime_utc=datetime(2026, 2, 18, 20, 0, 0, tzinfo=UTC),
                promoter_owner_address="rPromoterE2E",
                fighter_a_destination="rFighterE2EA",
                fighter_b_destination="rFighterE2EB",
                show_a_drops=2_000_000,
                show_b_drops=2_100_000,
                bonus_a_drops=300_000,
                bonus_b_drops=300_000,
            )
            session.commit()
            return bout.id

    def _build_escrow_confirm_payload(
        self,
        *,
        escrow_kind: EscrowKind,
        tx_hash: str,
        offer_sequence: int,
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
            return {
                "escrow_kind": escrow_kind.value,
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

    def _build_payout_confirm_payload(
        self,
        *,
        escrow_kind: EscrowKind,
        tx_hash: str,
        transaction_type: str,
    ) -> dict[str, object]:
        with Session(self.engine) as session:
            escrow = session.scalar(
                select(Escrow).where(
                    Escrow.bout_id == self.bout_id,
                    Escrow.kind == escrow_kind,
                )
            )
            assert escrow is not None
            assert escrow.offer_sequence is not None
            return {
                "escrow_kind": escrow_kind.value,
                "tx_hash": tx_hash,
                "validated": True,
                "engine_result": "tesSUCCESS",
                "transaction_type": transaction_type,
                "owner_address": escrow.owner_address,
                "offer_sequence": escrow.offer_sequence,
                "close_time_ripple": escrow.finish_after_ripple + 1,
                "fulfillment_hex": escrow.encrypted_preimage_hex if escrow_kind == EscrowKind.BONUS_A else None,
            }

    def _assert_sign_request_shape(self, sign_request: dict[str, object]) -> None:
        self.assertIsInstance(sign_request.get("payload_id"), str)
        self.assertIsInstance(sign_request.get("deep_link_url"), str)
        self.assertIsInstance(sign_request.get("qr_png_url"), str)
        self.assertIn(sign_request.get("mode"), {"stub", "api"})
        deep_link_url = str(sign_request["deep_link_url"])
        qr_png_url = str(sign_request["qr_png_url"])
        self.assertTrue(deep_link_url.startswith("xumm://payload/"))
        self.assertTrue(qr_png_url.startswith("https://xumm.app/sign/"))

    def _auth_headers(self, token: str, *, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {token}"}
        if extra:
            headers.update(extra)
        return headers

    def _override_get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
