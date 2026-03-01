from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.db.uow import SqlAlchemyUnitOfWork
from app.integrations.xaman_service import XamanIntegrationError, XamanService
from app.schemas.xaman import XamanSignRequestView


def store_idempotent_result(
    *,
    callback: Callable[..., None],
    scope: str,
    idempotency_key: str,
    request_hash: str,
    status_code: int,
    response_body: dict[str, Any],
) -> None:
    callback(
        scope=scope,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        status_code=status_code,
        response_body=response_body,
    )


def commit_or_raise_persistence_error(*, uow: SqlAlchemyUnitOfWork, detail: str) -> None:
    try:
        uow.commit()
    except IntegrityError as exc:
        uow.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc


def create_xaman_sign_request_view(
    *,
    xaman: XamanService,
    tx_json: dict[str, Any],
    reference: str,
) -> XamanSignRequestView:
    try:
        sign_request = xaman.create_sign_request(tx_json=tx_json, reference=reference)
    except XamanIntegrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Xaman signing request could not be prepared.",
        ) from exc
    return XamanSignRequestView(
        payload_id=sign_request.payload_id,
        deep_link_url=sign_request.deep_link_url,
        qr_png_url=sign_request.qr_png_url,
        websocket_status_url=sign_request.websocket_status_url,
        mode=sign_request.mode,
    )
