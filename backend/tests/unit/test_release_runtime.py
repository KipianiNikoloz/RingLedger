from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


@pytest.mark.parametrize(
    ("override", "error"),
    [
        ({"JWT_SECRET": "short"}, "unsafe_jwt_secret"),
        ({"XAMAN_MODE": "stub"}, "production_requires_xaman_api"),
        ({"DB_AUTO_MIGRATE_ON_STARTUP": "true"}, "production_auto_migrate_forbidden"),
        ({"CORS_ORIGINS": "*"}, "production_wildcard_cors_forbidden"),
        ({"XRPL_EXPECTED_NETWORK_ID": "0"}, "production_requires_xrpl_testnet"),
    ],
)
def test_production_rejects_unsafe_configuration(override: dict[str, str], error: str) -> None:
    safe = {
        "APP_ENV": "production",
        "JWT_SECRET": "a-production-secret-that-is-at-least-32-characters",
        "XAMAN_MODE": "api",
        "XAMAN_API_KEY": "key",
        "XAMAN_API_SECRET": "secret",
        "DB_AUTO_MIGRATE_ON_STARTUP": "false",
        "CORS_ORIGINS": "https://ringledger.example.com",
        "XRPL_RPC_URL": "https://s.altnet.rippletest.net:51234",
        "XRPL_EXPECTED_NETWORK_ID": "1",
    }
    with patch.dict("os.environ", safe | override, clear=True), pytest.raises(ValueError, match=error):
        get_settings()


def test_health_and_readiness_are_separate(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main

    monkeypatch.setattr(main, "init_db", lambda: None)
    monkeypatch.setattr(main, "check_database_ready", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    app = main.create_app()
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["detail"] == {"status": "not_ready", "database": "unavailable"}
