from __future__ import annotations

import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.integrations.xaman_service import XamanService
from app.main import create_app
from app.services.failure_taxonomy import classify_confirmation_failure


class M4PerformanceBaselineTests(unittest.TestCase):
    HEALTHZ_REQUEST_COUNT = 250
    HEALTHZ_THRESHOLD_SECONDS = 10.0
    XAMAN_SIGN_REQUEST_COUNT = 1_000
    XAMAN_SIGN_REQUEST_THRESHOLD_SECONDS = 8.0
    FAILURE_CLASSIFICATION_COUNT = 120_000
    FAILURE_CLASSIFICATION_THRESHOLD_SECONDS = 4.0

    @patch("app.main.init_db")
    def test_healthz_response_loop_baseline(self, init_db_mock: object) -> None:
        app = create_app()
        with TestClient(app) as client:
            started = time.perf_counter()
            for _ in range(self.HEALTHZ_REQUEST_COUNT):
                response = client.get("/healthz")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"status": "ok"})
            elapsed = time.perf_counter() - started

        self.assertLess(
            elapsed,
            self.HEALTHZ_THRESHOLD_SECONDS,
            msg=(
                f"healthz loop exceeded baseline: {elapsed:.4f}s > "
                f"{self.HEALTHZ_THRESHOLD_SECONDS:.1f}s for {self.HEALTHZ_REQUEST_COUNT} requests"
            ),
        )
        init_db_mock.assert_called_once()

    def test_xaman_stub_sign_request_generation_baseline(self) -> None:
        service = XamanService(
            mode="stub",
            api_base_url="https://xumm.app",
            api_key=None,
            api_secret=None,
            timeout_seconds=10,
        )
        tx_json = {
            "TransactionType": "EscrowCreate",
            "Account": "rPerfPromoter",
            "Destination": "rPerfFighter",
            "Amount": "250000",
            "FinishAfter": 823000000,
        }

        started = time.perf_counter()
        for i in range(self.XAMAN_SIGN_REQUEST_COUNT):
            sign_request = service.create_sign_request(tx_json=tx_json, reference=f"perf-sign-{i}")
            self.assertEqual(sign_request.mode, "stub")
            self.assertTrue(sign_request.deep_link_url.startswith("xumm://payload/"))
        elapsed = time.perf_counter() - started

        self.assertLess(
            elapsed,
            self.XAMAN_SIGN_REQUEST_THRESHOLD_SECONDS,
            msg=(
                f"xaman sign-request baseline exceeded: {elapsed:.4f}s > "
                f"{self.XAMAN_SIGN_REQUEST_THRESHOLD_SECONDS:.1f}s for {self.XAMAN_SIGN_REQUEST_COUNT} iterations"
            ),
        )

    def test_failure_taxonomy_classification_baseline(self) -> None:
        outcomes: dict[str, int] = {}
        started = time.perf_counter()
        for i in range(self.FAILURE_CLASSIFICATION_COUNT):
            mode = i % 4
            if mode == 0:
                validation_error = "ledger_tx_not_success"
                validated = False
                engine_result = "declined"
            elif mode == 1:
                validation_error = "ledger_tx_not_validated"
                validated = False
                engine_result = "timeout"
            elif mode == 2:
                validation_error = "ledger_tx_not_success"
                validated = True
                engine_result = "tecUNFUNDED_OFFER"
            else:
                validation_error = "invariant_mismatch"
                validated = True
                engine_result = "tesSUCCESS"

            code = classify_confirmation_failure(
                validation_error=validation_error,
                validated=validated,
                engine_result=engine_result,
            )
            outcomes[code] = outcomes.get(code, 0) + 1
        elapsed = time.perf_counter() - started

        self.assertLess(
            elapsed,
            self.FAILURE_CLASSIFICATION_THRESHOLD_SECONDS,
            msg=(
                f"failure taxonomy baseline exceeded: {elapsed:.4f}s > "
                f"{self.FAILURE_CLASSIFICATION_THRESHOLD_SECONDS:.1f}s for "
                f"{self.FAILURE_CLASSIFICATION_COUNT} classifications"
            ),
        )
        self.assertEqual(sum(outcomes.values()), self.FAILURE_CLASSIFICATION_COUNT)
        self.assertGreater(outcomes.get("signing_declined", 0), 0)
        self.assertGreater(outcomes.get("confirmation_timeout", 0), 0)
        self.assertGreater(outcomes.get("ledger_tec_tem", 0), 0)
        self.assertGreater(outcomes.get("invalid_confirmation", 0), 0)


if __name__ == "__main__":
    unittest.main()
