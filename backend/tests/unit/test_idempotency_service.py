from __future__ import annotations

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.services.idempotency_service import IdempotencyKeyMismatchError, IdempotencyService


class IdempotencyServiceUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_replay_returns_stored_response_for_same_hash(self) -> None:
        with Session(self.engine) as session:
            service = IdempotencyService(session=session)
            payload = {"escrow_kind": "show_a", "tx_hash": "ABC123456789"}
            request_hash = service.hash_request_payload(payload)
            service.store_response(
                scope="escrow_create_confirm:demo-bout",
                idempotency_key="key-1",
                request_hash=request_hash,
                status_code=200,
                response_body={"detail": "ok"},
            )
            session.commit()

            replay = service.load_replay(
                scope="escrow_create_confirm:demo-bout",
                idempotency_key="key-1",
                request_hash=request_hash,
            )
            assert replay is not None
            self.assertEqual(replay.status_code, 200)
            self.assertEqual(replay.response_body, {"detail": "ok"})

    def test_replay_rejects_payload_hash_mismatch(self) -> None:
        with Session(self.engine) as session:
            service = IdempotencyService(session=session)
            first_hash = service.hash_request_payload({"escrow_kind": "show_a", "tx_hash": "ABC123456789"})
            second_hash = service.hash_request_payload({"escrow_kind": "show_a", "tx_hash": "XYZ123456789"})
            service.store_response(
                scope="escrow_create_confirm:demo-bout",
                idempotency_key="key-2",
                request_hash=first_hash,
                status_code=200,
                response_body={"detail": "ok"},
            )
            session.commit()

            with self.assertRaises(IdempotencyKeyMismatchError):
                service.load_replay(
                    scope="escrow_create_confirm:demo-bout",
                    idempotency_key="key-2",
                    request_hash=second_hash,
                )


if __name__ == "__main__":
    unittest.main()
