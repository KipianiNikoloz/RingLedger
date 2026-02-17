from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str
    jwt_secret: str
    jwt_exp_minutes: int


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "FightPurse API"),
        database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://fightpurse:fightpurse@localhost:5432/fightpurse"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me-in-production"),
        jwt_exp_minutes=int(os.getenv("JWT_EXP_MINUTES", "60")),
    )


settings = get_settings()
