from __future__ import annotations

import importlib
import unittest


class AuthApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_auth_routes_exist(self) -> None:
        from app.main import app

        paths = app.openapi()["paths"]
        self.assertIn("post", paths["/auth/register"])
        self.assertIn("post", paths["/auth/login"])
        self.assertNotIn("/auth/wallet-login", paths)


if __name__ == "__main__":
    unittest.main()
