from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.middleware.idempotency import build_confirm_scope, require_idempotency_key
from app.models.enums import UserRole
from app.schemas.escrow import (
    EscrowConfirmRequest,
    EscrowConfirmResponse,
    EscrowPrepareItem,
    EscrowPrepareResponse,
)
from app.schemas.payout import (
    BoutResultRequest,
    BoutResultResponse,
    PayoutConfirmRequest,
    PayoutConfirmResponse,
    PayoutPrepareItem,
    PayoutPrepareResponse,
)
from app.services.escrow_service import EscrowService
from app.services.idempotency_service import IdempotencyKeyMismatchError, IdempotencyService
from app.services.payout_service import PayoutService
from app.services.xrpl_escrow_service import EscrowCreateConfirmation, EscrowPayoutConfirmation

router = APIRouter(prefix="/bouts", tags=["bouts"])

_ESCROW_CREATE_CONFLICT_ERRORS = {
    "bout_not_in_draft_state",
    "escrow_not_planned",
}
_ESCROW_CREATE_UNPROCESSABLE_CONFIRMATION_ERRORS = {
    "ledger_tx_not_validated",
    "ledger_tx_not_success",
    "ledger_owner_address_mismatch",
    "ledger_destination_address_mismatch",
    "ledger_amount_mismatch",
    "ledger_finish_after_mismatch",
    "ledger_cancel_after_mismatch",
    "ledger_condition_mismatch",
}
_RESULT_CONFLICT_ERRORS = {
    "bout_not_in_escrows_created_state",
}
_PAYOUT_PREPARE_CONFLICT_ERRORS = {
    "bout_not_preparable_for_payout",
    "escrow_not_preparable_for_payout",
    "bout_winner_not_set",
}
_PAYOUT_CONFIRM_CONFLICT_ERRORS = {
    "bout_not_in_payout_state",
    "escrow_not_created",
    "bout_winner_not_set",
}
_PAYOUT_UNPROCESSABLE_CONFIRMATION_ERRORS = {
    "ledger_tx_not_validated",
    "ledger_tx_not_success",
    "ledger_owner_address_mismatch",
    "ledger_offer_sequence_mismatch",
    "ledger_transaction_type_mismatch",
    "ledger_finish_before_allowed",
    "ledger_cancel_before_allowed",
    "ledger_cancel_after_missing",
    "ledger_fulfillment_mismatch",
    "ledger_unexpected_fulfillment",
}


@router.post("/{bout_id}/escrows/prepare", response_model=EscrowPrepareResponse)
def prepare_escrow_create_payloads(
    bout_id: uuid.UUID,
    _actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
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
    _actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
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
        code, body = _map_escrow_create_confirm_error(str(exc))
        _store_idempotent_result(
            callback=idem.store_response,
            scope=scope,
            idempotency_key=key,
            request_hash=request_hash,
            status_code=code,
            response_body=body,
        )
        _commit_or_raise_persistence_error(
            session=session,
            detail="Escrow confirmation could not be persisted safely.",
        )
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
    _commit_or_raise_persistence_error(
        session=session,
        detail="Escrow confirmation could not be persisted safely.",
    )
    return response


@router.post("/{bout_id}/result", response_model=BoutResultResponse)
def enter_bout_result(
    bout_id: uuid.UUID,
    payload: BoutResultRequest,
    actor: RequestActor = Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_session),
) -> BoutResultResponse:
    service = PayoutService(session=session)
    try:
        bout = service.enter_bout_result(
            bout_id=bout_id,
            winner=payload.winner,
            actor_user_id=actor.user_id,
        )
    except ValueError as exc:
        code, body = _map_result_error(str(exc))
        raise HTTPException(status_code=code, detail=body["detail"]) from exc

    _commit_or_raise_persistence_error(session=session, detail="Bout result could not be persisted safely.")
    return BoutResultResponse(
        bout_id=str(bout.id),
        bout_status=bout.status,
        winner=bout.winner or payload.winner,
    )


@router.post("/{bout_id}/payouts/prepare", response_model=PayoutPrepareResponse)
def prepare_payout_payloads(
    bout_id: uuid.UUID,
    _actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> PayoutPrepareResponse:
    service = PayoutService(session=session)
    try:
        bout, items = service.prepare_payout_payloads(bout_id=bout_id)
    except ValueError as exc:
        code, body = _map_payout_prepare_error(str(exc))
        raise HTTPException(status_code=code, detail=body["detail"]) from exc

    return PayoutPrepareResponse(
        bout_id=str(bout.id),
        bout_status=bout.status,
        escrows=[
            PayoutPrepareItem(
                escrow_id=item["escrow_id"],
                escrow_kind=item["escrow_kind"],
                action=item["action"],
                unsigned_tx=item["unsigned_tx"],
            )
            for item in items
        ],
    )


@router.post("/{bout_id}/payouts/confirm", response_model=PayoutConfirmResponse)
def confirm_payout(
    bout_id: uuid.UUID,
    payload: PayoutConfirmRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    _actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> PayoutConfirmResponse | JSONResponse:
    key = require_idempotency_key(idempotency_key)
    idem = IdempotencyService(session=session)
    request_payload = payload.model_dump(mode="json")
    request_hash = idem.hash_request_payload(request_payload)
    scope = build_confirm_scope(operation="payout_confirm", bout_id=bout_id)

    try:
        replay = idem.load_replay(scope=scope, idempotency_key=key, request_hash=request_hash)
    except IdempotencyKeyMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key was already used with a different request payload.",
        ) from exc

    if replay is not None:
        return JSONResponse(status_code=replay.status_code, content=replay.response_body)

    service = PayoutService(session=session)
    confirmation = EscrowPayoutConfirmation(
        tx_hash=payload.tx_hash,
        validated=payload.validated,
        engine_result=payload.engine_result,
        transaction_type=payload.transaction_type,
        owner_address=payload.owner_address,
        offer_sequence=payload.offer_sequence,
        close_time_ripple=payload.close_time_ripple,
        fulfillment_hex=payload.fulfillment_hex,
    )

    try:
        bout, escrow = service.confirm_payout(
            bout_id=bout_id,
            escrow_kind=payload.escrow_kind,
            confirmation=confirmation,
        )
    except ValueError as exc:
        code, body = _map_payout_confirm_error(str(exc))
        _store_idempotent_result(
            callback=idem.store_response,
            scope=scope,
            idempotency_key=key,
            request_hash=request_hash,
            status_code=code,
            response_body=body,
        )
        _commit_or_raise_persistence_error(
            session=session,
            detail="Payout confirmation could not be persisted safely.",
        )
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        session.rollback()
        raise

    response = PayoutConfirmResponse(
        bout_id=str(bout.id),
        escrow_id=str(escrow.id),
        escrow_kind=escrow.kind,
        escrow_status=escrow.status,
        bout_status=bout.status,
        tx_hash=escrow.close_tx_hash or "",
    )
    _store_idempotent_result(
        callback=idem.store_response,
        scope=scope,
        idempotency_key=key,
        request_hash=request_hash,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    _commit_or_raise_persistence_error(
        session=session,
        detail="Payout confirmation could not be persisted safely.",
    )
    return response


def _map_escrow_create_confirm_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in {"bout_not_found", "escrow_not_found"}:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code in _ESCROW_CREATE_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Escrow confirmation is not allowed in current state."}
    if error_code in _ESCROW_CREATE_UNPROCESSABLE_CONFIRMATION_ERRORS:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Ledger confirmation failed validation."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Escrow confirmation request is invalid."}


def _map_result_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code == "bout_not_found":
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout was not found."}
    if error_code in _RESULT_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Bout result cannot be entered in current state."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Bout result request is invalid."}


def _map_payout_prepare_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code == "bout_not_found":
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout was not found."}
    if error_code in _PAYOUT_PREPARE_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Payout prepare is not allowed in current state."}
    if error_code in {"bout_escrow_set_invalid", "winner_bonus_fulfillment_missing"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Payout setup is invalid."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Payout prepare request is invalid."}


def _map_payout_confirm_error(error_code: str) -> tuple[int, dict[str, Any]]:
    if error_code in {"bout_not_found", "escrow_not_found"}:
        return status.HTTP_404_NOT_FOUND, {"detail": "Requested bout/escrow was not found."}
    if error_code in _PAYOUT_CONFIRM_CONFLICT_ERRORS:
        return status.HTTP_409_CONFLICT, {"detail": "Payout confirmation is not allowed in current state."}
    if error_code in _PAYOUT_UNPROCESSABLE_CONFIRMATION_ERRORS:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Ledger confirmation failed validation."}
    if error_code in {"winner_bonus_fulfillment_missing", "bout_escrow_set_invalid"}:
        return status.HTTP_422_UNPROCESSABLE_CONTENT, {"detail": "Payout setup is invalid."}
    return status.HTTP_400_BAD_REQUEST, {"detail": "Payout confirmation request is invalid."}


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


def _commit_or_raise_persistence_error(*, session: Session, detail: str) -> None:
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc
