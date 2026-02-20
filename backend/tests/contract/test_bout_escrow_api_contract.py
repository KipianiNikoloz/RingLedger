from __future__ import annotations

import importlib
import unittest


class BoutEscrowApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_bout_lifecycle_routes_exist(self) -> None:
        from app.main import app

        routes = {(route.path, tuple(route.methods)) for route in app.routes}
        self.assertTrue(
            any(path == "/bouts/{bout_id}/escrows/prepare" and "POST" in methods for path, methods in routes)
        )
        self.assertTrue(
            any(path == "/bouts/{bout_id}/escrows/confirm" and "POST" in methods for path, methods in routes)
        )
        self.assertTrue(any(path == "/bouts/{bout_id}/result" and "POST" in methods for path, methods in routes))
        self.assertTrue(
            any(path == "/bouts/{bout_id}/payouts/prepare" and "POST" in methods for path, methods in routes)
        )
        self.assertTrue(
            any(path == "/bouts/{bout_id}/payouts/confirm" and "POST" in methods for path, methods in routes)
        )


if __name__ == "__main__":
    unittest.main()
