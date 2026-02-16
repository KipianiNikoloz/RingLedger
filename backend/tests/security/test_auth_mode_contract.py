from __future__ import annotations

import importlib
import sys
from pathlib import Path
import unittest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class AuthModeContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_wallet_login_route_does_not_exist(self) -> None:
        from app.main import app

        route_paths = [route.path for route in app.routes]
        self.assertNotIn("/auth/wallet-login", route_paths)
        self.assertNotIn("/wallet/login", route_paths)


if __name__ == "__main__":
    unittest.main()

