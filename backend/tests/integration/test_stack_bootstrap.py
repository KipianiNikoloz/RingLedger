from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import create_app


class StackBootstrapIntegrationTests(unittest.TestCase):
    @patch("app.main.init_db")
    def test_application_bootstrap_with_database(self, init_db_mock: object) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        init_db_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
