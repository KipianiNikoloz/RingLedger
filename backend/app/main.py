from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import engine
from app.integrations.xrpl_client import XrplClient


def check_database_ready() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def check_xrpl_ready() -> None:
    XrplClient(
        rpc_url=settings.xrpl_rpc_url,
        expected_network_id=settings.xrpl_expected_network_id,
        timeout_seconds=settings.xrpl_timeout_seconds,
    ).check_network()


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        init_db()
        yield

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["health"])
    def readyz() -> dict[str, str]:
        try:
            check_database_ready()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "database": "unavailable"},
            ) from exc
        try:
            check_xrpl_ready()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "database": "ready", "xrpl": "unavailable"},
            ) from exc
        return {"status": "ready", "database": "ready", "xrpl": "testnet"}

    app.include_router(api_router)
    return app


app = create_app()
