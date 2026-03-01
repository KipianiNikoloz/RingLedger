from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.integrations.xaman_service import XamanIntegrationError
from app.models.enums import UserRole
from app.schemas.signing import SigningReconcileRequest, SigningReconcileResponse
from app.services.signing_reconciliation_service import (
    SigningReconciliationOutcome,
    SigningReconciliationService,
)

from .error_map import map_signing_reconcile_error
from .http_utils import commit_or_raise_persistence_error

router = APIRouter()


@router.post("/{bout_id}/escrows/signing/reconcile", response_model=SigningReconcileResponse)
def reconcile_escrow_signing_status(
    bout_id: uuid.UUID,
    payload: SigningReconcileRequest,
    actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> SigningReconcileResponse:
    return _reconcile_signing(
        session=session,
        action=lambda service: service.reconcile_escrow_create_signing(
            bout_id=bout_id,
            escrow_kind=payload.escrow_kind,
            payload_id=payload.payload_id,
            actor_user_id=actor.user_id,
            observed_status=payload.observed_status,
            observed_tx_hash=payload.observed_tx_hash,
        ),
        persistence_error_detail="Escrow signing reconciliation could not be persisted safely.",
    )


@router.post("/{bout_id}/payouts/signing/reconcile", response_model=SigningReconcileResponse)
def reconcile_payout_signing_status(
    bout_id: uuid.UUID,
    payload: SigningReconcileRequest,
    actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> SigningReconcileResponse:
    return _reconcile_signing(
        session=session,
        action=lambda service: service.reconcile_payout_signing(
            bout_id=bout_id,
            escrow_kind=payload.escrow_kind,
            payload_id=payload.payload_id,
            actor_user_id=actor.user_id,
            observed_status=payload.observed_status,
            observed_tx_hash=payload.observed_tx_hash,
        ),
        persistence_error_detail="Payout signing reconciliation could not be persisted safely.",
    )


def _reconcile_signing(
    *,
    session: Session,
    action: Callable[[SigningReconciliationService], SigningReconciliationOutcome],
    persistence_error_detail: str,
) -> SigningReconcileResponse:
    uow = SqlAlchemyUnitOfWork(session=session)
    service = SigningReconciliationService(session=session)
    try:
        outcome = action(service)
    except ValueError as exc:
        uow.rollback()
        code, body = map_signing_reconcile_error(str(exc))
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except XamanIntegrationError as exc:
        uow.rollback()
        code, body = map_signing_reconcile_error(str(exc))
        raise HTTPException(status_code=code, detail=body["detail"]) from exc
    except Exception:
        uow.rollback()
        raise

    commit_or_raise_persistence_error(
        uow=uow,
        detail=persistence_error_detail,
    )
    return SigningReconcileResponse(
        bout_id=str(outcome.bout.id),
        escrow_id=str(outcome.escrow.id),
        escrow_kind=outcome.escrow.kind,
        escrow_status=outcome.escrow.status,
        payload_id=outcome.payload_id,
        signing_status=outcome.signing_status.value,
        tx_hash=outcome.tx_hash,
        failure_code=outcome.escrow.failure_code,
    )
