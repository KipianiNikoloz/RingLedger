from __future__ import annotations

import importlib
import unittest


class FighterProfileApiContractTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("fastapi") is not None, "fastapi is not installed")
    def test_fighter_profile_route_exists(self) -> None:
        from app.main import app

        routes = {(route.path, tuple(route.methods)) for route in app.routes}
        self.assertTrue(any(path == "/fighters/me" and "PUT" in methods for path, methods in routes))


if __name__ == "__main__":
    unittest.main()
