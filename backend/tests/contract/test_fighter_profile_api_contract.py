from __future__ import annotations

import importlib
import unittest


class FighterProfileApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_fighter_profile_route_exists(self) -> None:
        from app.main import app

        self.assertIn("put", app.openapi()["paths"]["/fighters/me"])


if __name__ == "__main__":
    unittest.main()
