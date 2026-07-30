from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    database_url: str
    db_auto_migrate_on_startup: bool
    jwt_secret: str
    jwt_exp_minutes: int
    xaman_mode: str
    xaman_api_base_url: str
    xaman_api_key: str | None
    xaman_api_secret: str | None
    xaman_timeout_seconds: int
    xrpl_rpc_url: str
    xrpl_expected_network_id: int
    xrpl_timeout_seconds: int
    cors_origins: tuple[str, ...]


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"invalid_boolean:{value}")


def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    auto_migrate_default = "true" if app_env in {"development", "dev", "local", "test"} else "false"
    xaman_mode = os.getenv("XAMAN_MODE", "stub").strip().lower()
    configured = Settings(
        app_name=os.getenv("APP_NAME", "FightPurse API"),
        app_env=app_env,
        database_url=_secret("DATABASE_URL", "postgresql+psycopg://fightpurse:fightpurse@localhost:5432/fightpurse"),
        db_auto_migrate_on_startup=_parse_bool(os.getenv("DB_AUTO_MIGRATE_ON_STARTUP", auto_migrate_default)),
        jwt_secret=_secret("JWT_SECRET", "change-me-in-production-min-32-chars"),
        jwt_exp_minutes=int(os.getenv("JWT_EXP_MINUTES", "60")),
        xaman_mode=xaman_mode,
        xaman_api_base_url=os.getenv("XAMAN_API_BASE_URL", "https://xumm.app").strip(),
        xaman_api_key=_secret("XAMAN_API_KEY") or None,
        xaman_api_secret=_secret("XAMAN_API_SECRET") or None,
        xaman_timeout_seconds=int(os.getenv("XAMAN_TIMEOUT_SECONDS", "10")),
        xrpl_rpc_url=os.getenv("XRPL_RPC_URL", "https://s.altnet.rippletest.net:51234").strip(),
        xrpl_expected_network_id=int(os.getenv("XRPL_EXPECTED_NETWORK_ID", "1")),
        xrpl_timeout_seconds=int(os.getenv("XRPL_TIMEOUT_SECONDS", "10")),
        cors_origins=tuple(
            origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()
        ),
    )
    _validate_settings(configured)
    return configured


def _secret(name: str, default: str = "") -> str:
    file_name = os.getenv(f"{name}_FILE")
    if file_name:
        return Path(file_name).read_text(encoding="utf-8").rstrip("\r\n")
    return os.getenv(name, default)


def _validate_settings(configured: Settings) -> None:
    if configured.app_env != "production":
        return
    if len(configured.jwt_secret) < 32 or configured.jwt_secret == "change-me-in-production-min-32-chars":
        raise ValueError("unsafe_jwt_secret")
    if configured.xaman_mode != "api" or not configured.xaman_api_key or not configured.xaman_api_secret:
        raise ValueError("production_requires_xaman_api")
    if configured.db_auto_migrate_on_startup:
        raise ValueError("production_auto_migrate_forbidden")
    if not configured.cors_origins or "*" in configured.cors_origins:
        raise ValueError("production_wildcard_cors_forbidden")
    if configured.xrpl_expected_network_id != 1 or not configured.xrpl_rpc_url.startswith("https://"):
        raise ValueError("production_requires_xrpl_testnet")


settings = get_settings()
