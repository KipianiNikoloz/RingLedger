from __future__ import annotations

import importlib
import unittest


class BoutEscrowApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_bout_lifecycle_routes_exist(self) -> None:
        from app.main import app

        paths = app.openapi()["paths"]
        expected = {
            "/bouts": {"get", "post"},
            "/bouts/{bout_id}": {"get"},
            "/bouts/{bout_id}/escrows/prepare": {"post"},
            "/bouts/{bout_id}/escrows/confirm": {"post"},
            "/bouts/{bout_id}/escrows/signing/reconcile": {"post"},
            "/bouts/{bout_id}/result": {"post"},
            "/bouts/{bout_id}/payouts/prepare": {"post"},
            "/bouts/{bout_id}/payouts/confirm": {"post"},
            "/bouts/{bout_id}/payouts/signing/reconcile": {"post"},
        }
        for path, methods in expected.items():
            self.assertTrue(methods.issubset(paths[path]))

    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_confirmation_requests_only_accept_kind_and_transaction_hash(self) -> None:
        from app.main import app

        schemas = app.openapi()["components"]["schemas"]
        for schema_name in ("EscrowConfirmRequest", "PayoutConfirmRequest"):
            schema = schemas[schema_name]
            self.assertEqual(set(schema["properties"]), {"escrow_kind", "tx_hash"})
            self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
