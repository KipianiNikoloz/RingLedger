from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.integrations.xaman_service import XamanService
from app.models.enums import UserRole
from app.schemas.payout import (
    BoutResultRequest,
    BoutResultResponse,
    PayoutConfirmRequest,
    PayoutConfirmResponse,
    PayoutPrepareItem,
    PayoutPrepareResponse,
)
from app.services.payout_service import PayoutService
from app.services.xrpl_escrow_service import EscrowPayoutConfirmation

from .confirm_flow import (
    persist_confirm_failure,
    persist_confirm_success,
    prepare_confirm_flow,
)
from .error_map import (
    map_payout_confirm_error,
    map_payout_prepare_error,
    map_result_error,
)
from .http_utils import commit_or_raise_persistence_error, create_xaman_sign_request_view

router = APIRouter()


@router.post("/{bout_id}/result", response_model=BoutResultResponse)
def enter_bout_result(
    bout_id: uuid.UUID,
    payload: BoutResultRequest,
    actor: RequestActor = Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_session),
) -> BoutResultResponse:
    uow = SqlAlchemyUnitOfWork(session=session)
    service = PayoutService(session=session)
    try:
        bout = service.enter_bout_result(
            bout_id=bout_id,
            winner=payload.winner,
            actor_user_id=actor.user_id,
        )
    except ValueError as exc:
        uow.rollback()
        code, body = map_result_error(str(exc))
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        uow.rollback()
        raise

    commit_or_raise_persistence_error(uow=uow, detail="Bout result could not be persisted safely.")
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
    xaman = XamanService.from_settings()
    try:
        bout, items = service.prepare_payout_payloads(bout_id=bout_id)
    except ValueError as exc:
        code, body = map_payout_prepare_error(str(exc))
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
                xaman_sign_request=create_xaman_sign_request_view(
                    xaman=xaman,
                    tx_json=item["unsigned_tx"],
                    reference=f"payout_prepare:{bout.id}:{item['escrow_id']}:{item['action']}",
                ),
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
    context, replay = prepare_confirm_flow(
        session=session,
        idempotency_key_header=idempotency_key,
        request_payload=payload.model_dump(mode="json"),
        operation="payout_confirm",
        bout_id=bout_id,
    )
    if replay is not None:
        return replay

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
        code, body = map_payout_confirm_error(str(exc))
        persist_confirm_failure(
            context=context,
            status_code=code,
            response_body=body,
            persistence_error_detail="Payout confirmation could not be persisted safely.",
        )
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        context.uow.rollback()
        raise

    response = PayoutConfirmResponse(
        bout_id=str(bout.id),
        escrow_id=str(escrow.id),
        escrow_kind=escrow.kind,
        escrow_status=escrow.status,
        bout_status=bout.status,
        tx_hash=escrow.close_tx_hash or "",
    )
    persist_confirm_success(
        context=context,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
        persistence_error_detail="Payout confirmation could not be persisted safely.",
    )
    return response
