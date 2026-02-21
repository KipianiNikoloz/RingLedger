from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command
from app.core.config import settings


def _build_alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def run_db_migrations(*, revision: str = "head") -> None:
    command.upgrade(_build_alembic_config(), revision)


def init_db() -> None:
    """Run startup migrations according to runtime safety policy."""
    if settings.app_env == "production":
        return
    if not settings.db_auto_migrate_on_startup:
        return
    run_db_migrations(revision="head")
