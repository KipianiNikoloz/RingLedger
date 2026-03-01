from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.uow import SqlAlchemyUnitOfWork
from app.middleware.idempotency import build_confirm_scope, require_idempotency_key
from app.services.idempotency_service import IdempotencyKeyMismatchError, IdempotencyService

from .http_utils import commit_or_raise_persistence_error, store_idempotent_result


@dataclass(frozen=True)
class ConfirmFlowContext:
    uow: SqlAlchemyUnitOfWork
    idem: IdempotencyService
    key: str
    request_hash: str
    scope: str


def prepare_confirm_flow(
    *,
    session: Session,
    idempotency_key_header: str | None,
    request_payload: dict[str, Any],
    operation: str,
    bout_id: uuid.UUID,
) -> tuple[ConfirmFlowContext, JSONResponse | None]:
    uow = SqlAlchemyUnitOfWork(session=session)
    key = require_idempotency_key(idempotency_key_header)
    idem = IdempotencyService(session=session)
    request_hash = idem.hash_request_payload(request_payload)
    scope = build_confirm_scope(operation=operation, bout_id=bout_id)
    context = ConfirmFlowContext(
        uow=uow,
        idem=idem,
        key=key,
        request_hash=request_hash,
        scope=scope,
    )

    try:
        replay = idem.load_replay(scope=scope, idempotency_key=key, request_hash=request_hash)
    except IdempotencyKeyMismatchError as exc:
        uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key was already used with a different request payload.",
        ) from exc

    if replay is not None:
        return context, JSONResponse(status_code=replay.status_code, content=replay.response_body)
    return context, None


def persist_confirm_failure(
    *,
    context: ConfirmFlowContext,
    status_code: int,
    response_body: dict[str, Any],
    persistence_error_detail: str,
) -> None:
    store_idempotent_result(
        callback=context.idem.store_response,
        scope=context.scope,
        idempotency_key=context.key,
        request_hash=context.request_hash,
        status_code=status_code,
        response_body=response_body,
    )
    commit_or_raise_persistence_error(
        uow=context.uow,
        detail=persistence_error_detail,
    )


def persist_confirm_success(
    *,
    context: ConfirmFlowContext,
    status_code: int,
    response_body: dict[str, Any],
    persistence_error_detail: str,
) -> None:
    store_idempotent_result(
        callback=context.idem.store_response,
        scope=context.scope,
        idempotency_key=context.key,
        request_hash=context.request_hash,
        status_code=status_code,
        response_body=response_body,
    )
    commit_or_raise_persistence_error(
        uow=context.uow,
        detail=persistence_error_detail,
    )
