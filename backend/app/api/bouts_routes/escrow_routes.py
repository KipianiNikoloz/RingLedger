from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.integrations.xaman_service import XamanService
from app.models.enums import UserRole
from app.schemas.escrow import (
    EscrowConfirmRequest,
    EscrowConfirmResponse,
    EscrowPrepareItem,
    EscrowPrepareResponse,
)
from app.services.escrow_service import EscrowService
from app.services.xrpl_escrow_service import EscrowCreateConfirmation

from .confirm_flow import (
    persist_confirm_failure,
    persist_confirm_success,
    prepare_confirm_flow,
)
from .error_map import map_escrow_create_confirm_error
from .http_utils import create_xaman_sign_request_view

router = APIRouter()


@router.post("/{bout_id}/escrows/prepare", response_model=EscrowPrepareResponse)
def prepare_escrow_create_payloads(
    bout_id: uuid.UUID,
    _actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> EscrowPrepareResponse:
    service = EscrowService(session=session)
    xaman = XamanService.from_settings()
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
                xaman_sign_request=create_xaman_sign_request_view(
                    xaman=xaman,
                    tx_json=item["unsigned_tx"],
                    reference=f"escrow_create_prepare:{bout.id}:{item['escrow_id']}",
                ),
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
    context, replay = prepare_confirm_flow(
        session=session,
        idempotency_key_header=idempotency_key,
        request_payload=payload.model_dump(mode="json"),
        operation="escrow_create_confirm",
        bout_id=bout_id,
    )
    if replay is not None:
        return replay

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
        code, body = map_escrow_create_confirm_error(str(exc))
        persist_confirm_failure(
            context=context,
            status_code=code,
            response_body=body,
            persistence_error_detail="Escrow confirmation could not be persisted safely.",
        )
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        context.uow.rollback()
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
    persist_confirm_success(
        context=context,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
        persistence_error_detail="Escrow confirmation could not be persisted safely.",
    )
    return response
