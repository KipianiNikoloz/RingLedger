from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.middleware.idempotency import build_confirm_scope, require_idempotency_key
from app.schemas.escrow import (
    EscrowConfirmRequest,
    EscrowConfirmResponse,
    EscrowPrepareItem,
    EscrowPrepareResponse,
)
from app.services.escrow_service import EscrowService
from app.services.idempotency_service import IdempotencyKeyMismatchError, IdempotencyService
from app.services.xrpl_escrow_service import EscrowCreateConfirmation

router = APIRouter(prefix="/bouts", tags=["bouts"])

_CONFLICT_ERRORS = {
    "bout_not_in_draft_state",
    "escrow_not_planned",
}
_UNPROCESSABLE_CONFIRMATION_ERRORS = {
    "ledger_tx_not_validated",
    "ledger_tx_not_success",
    "ledger_owner_address_mismatch",
    "ledger_destination_address_mismatch",
    "ledger_amount_mismatch",
    "ledger_finish_after_mismatch",
    "ledger_cancel_after_mismatch",
    "ledger_condition_mismatch",
}


@router.post("/{bout_id}/escrows/prepare", response_model=EscrowPrepareResponse)
def prepare_escrow_create_payloads(
    bout_id: uuid.UUID, session: Session = Depends(get_session)
) -> EscrowPrepareResponse:
    service = EscrowService(session=session)
    try:
        bout, items = service.prepare_escrow_create_payloads(bout_id=bout_id)
    except ValueError as exc:
        message = str(exc)
        if message == "bout_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bout was not found.") from exc
        if message in {"bout_not_preparable_for_escrow_create", "escrow_not_preparable_for_create"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Escrow create prepare is not allowed in the current state.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Bout escrow plan is invalid.",
        ) from exc

    return EscrowPrepareResponse(
        bout_id=str(bout.id),
        escrows=[
            EscrowPrepareItem(
                escrow_id=item["escrow_id"],
                escrow_kind=item["escrow_kind"],
                unsigned_tx=item["unsigned_tx"],
            )
            for item in items
        ],
    )


@router.post("/{bout_id}/escrows/confirm", response_model=EscrowConfirmResponse)
def confirm_escrow_create(
    bout_id: uuid.UUID,
    payload: EscrowConfirmRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    session: Session = Depends(get_session),
) -> EscrowConfirmResponse | JSONResponse:
    key = require_idempotency_key(idempotency_key)
    idem = IdempotencyService(session=session)
    request_payload = payload.model_dump(mode="json")
    request_hash = idem.hash_request_payload(request_payload)
    scope = build_confirm_scope(operation="escrow_create_confirm", bout_id=bout_id)

    try:
        replay = idem.load_replay(scope=scope, idempotency_key=key, request_hash=request_hash)
    except IdempotencyKeyMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key was already used with a different request payload.",
        ) from exc

    if replay is not None:
        return JSONResponse(status_code=replay.status_code, content=replay.response_body)

    service = EscrowService(session=session)
    confirmation = EscrowCreateConfirmation(
        tx_hash=payload.tx_hash,
        offer_sequence=payload.offer_sequence,
        validated=payload.validated,
        engine_result=payload.engine_result,
        owner_address=payload.owner_address,
        destination_address=payload.destination_address,
        amount_drops=payload.amount_drops,
        finish_after_ripple=payload.finish_after_ripple,
        cancel_after_ripple=payload.cancel_after_ripple,
        condition_hex=payload.condition_hex,
    )

    try:
        bout, escrow = service.confirm_escrow_create(
            bout_id=bout_id,
            escrow_kind=payload.escrow_kind,
            confirmation=confirmation,
        )
    except ValueError as exc:
        code, body = _map_confirm_error(str(exc))
        _store_idempotent_result(
            callback=idem.store_response,
            scope=scope,
            idempotency_key=key,
            request_hash=request_hash,
            status_code=code,
            response_body=body,
        )
        try:
            session.commit()
        except IntegrityError as commit_exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Escrow confirmation could not be persisted safely.",
            ) from commit_exc
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        session.rollback()
        raise

    response = EscrowConfirmResponse(
        bout_id=str(bout.id),
        escrow_id=str(escrow.id),
        escrow_kind=escrow.kind,
        escrow_status=escrow.status,
        bout_status=bout.status,
        tx_hash=escrow.create_tx_hash or "",
        offer_sequence=escrow.offer_sequence or 0,
    )
    _store_idempotent_result(
        callback=idem.store_response,
        scope=scope,
        idempotency_key=key,
        request_hash=request_hash,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Escrow confirmation could not be persisted safely.",
        ) from exc
    return response


def _map_confirm_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in {"bout_not_found", "escrow_not_found"}:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code in _CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Escrow confirmation is not allowed in current state."}
    if error_code in _UNPROCESSABLE_CONFIRMATION_ERRORS:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Ledger confirmation failed validation."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Escrow confirmation request is invalid."}


def _store_idempotent_result(
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
