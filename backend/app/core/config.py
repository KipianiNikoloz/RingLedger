from __future__ import annotations

import os
from dataclasses import dataclass


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
    return Settings(
        app_name=os.getenv("APP_NAME", "FightPurse API"),
        app_env=app_env,
        database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://fightpurse:fightpurse@localhost:5432/fightpurse"),
        db_auto_migrate_on_startup=_parse_bool(os.getenv("DB_AUTO_MIGRATE_ON_STARTUP", auto_migrate_default)),
        jwt_secret=os.getenv("JWT_SECRET", "change-me-in-production-min-32-chars"),
        jwt_exp_minutes=int(os.getenv("JWT_EXP_MINUTES", "60")),
        xaman_mode=xaman_mode,
        xaman_api_base_url=os.getenv("XAMAN_API_BASE_URL", "https://xumm.app").strip(),
        xaman_api_key=os.getenv("XAMAN_API_KEY") or None,
        xaman_api_secret=os.getenv("XAMAN_API_SECRET") or None,
        xaman_timeout_seconds=int(os.getenv("XAMAN_TIMEOUT_SECONDS", "10")),
    )


settings = get_settings()
