from __future__ import annotations

import importlib
import unittest


class AuthApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_auth_routes_exist(self) -> None:
        from app.main import app

        routes = {(route.path, tuple(route.methods)) for route in app.routes}
        self.assertTrue(any(path == "/auth/register" and "POST" in methods for path, methods in routes))
        self.assertTrue(any(path == "/auth/login" and "POST" in methods for path, methods in routes))
        self.assertFalse(any(path == "/auth/wallet-login" for path, _ in routes))


if __name__ == "__main__":
    unittest.main()
