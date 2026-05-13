from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, get_current_actor, require_role
from app.db.session import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.models.bout import Bout
from app.models.enums import UserRole
from app.models.escrow import Escrow
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository
from app.schemas.bout import BoutCreateRequest, BoutEscrowSummary, BoutListResponse, BoutSummaryResponse
from app.services.bout_service import BoutService

router = APIRouter(tags=["bouts"])


@router.post("/bouts", response_model=BoutSummaryResponse, status_code=status.HTTP_201_CREATED)
def create_bout(
    payload: BoutCreateRequest,
    actor: RequestActor = Depends(require_role(UserRole.PROMOTER)),
    session: Session = Depends(get_session),
) -> BoutSummaryResponse:
    uow = SqlAlchemyUnitOfWork(session=session)
    service = BoutService(session=session)
    try:
        bout = service.create_bout_draft_for_promoter(
            promoter_user_id=actor.user_id,
            fighter_a_user_id=payload.fighter_a_user_id,
            fighter_b_user_id=payload.fighter_b_user_id,
            event_datetime_utc=payload.event_datetime_utc,
            promoter_owner_address=payload.promoter_owner_address,
            show_a_drops=payload.show_a_drops,
            show_b_drops=payload.show_b_drops,
            bonus_a_drops=payload.bonus_a_drops,
            bonus_b_drops=payload.bonus_b_drops,
        )
        escrows = EscrowRepository(session=session).list_for_bout(bout_id=bout.id)
        response = _build_bout_summary(bout=bout, escrows=escrows)
        uow.commit()
        return response
    except ValueError as exc:
        uow.rollback()
        if str(exc) in {"fighter_not_found", "user_is_not_fighter", "fighter_profile_required"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Bout fighters must exist, have fighter role, and have fighter profiles.",
            ) from exc
        if str(exc) == "fighters_must_be_distinct":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Bout fighters must be distinct users.",
            ) from exc
        raise
    except IntegrityError as exc:
        uow.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create bout draft.") from exc
    except Exception:
        uow.rollback()
        raise


@router.get("/bouts", response_model=BoutListResponse)
def list_bouts(
    actor: RequestActor = Depends(get_current_actor),
    session: Session = Depends(get_session),
) -> BoutListResponse:
    bout_repository = BoutRepository(session=session)
    escrow_repository = EscrowRepository(session=session)
    bouts = bout_repository.list_visible_to_actor(user_id=actor.user_id, role=actor.role)
    return BoutListResponse(
        bouts=[
            _build_bout_summary(bout=bout, escrows=escrow_repository.list_for_bout(bout_id=bout.id)) for bout in bouts
        ]
    )


@router.get("/bouts/{bout_id}", response_model=BoutSummaryResponse)
def get_bout(
    bout_id: uuid.UUID,
    actor: RequestActor = Depends(get_current_actor),
    session: Session = Depends(get_session),
) -> BoutSummaryResponse:
    bout_repository = BoutRepository(session=session)
    bout = bout_repository.get_visible_to_actor(bout_id=bout_id, user_id=actor.user_id, role=actor.role)
    if bout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bout was not found.")
    return _build_bout_summary(bout=bout, escrows=EscrowRepository(session=session).list_for_bout(bout_id=bout.id))


def _build_bout_summary(*, bout: Bout, escrows: list[Escrow]) -> BoutSummaryResponse:
    return BoutSummaryResponse(
        bout_id=str(bout.id),
        promoter_user_id=str(bout.promoter_user_id),
        fighter_a_user_id=str(bout.fighter_a_user_id),
        fighter_b_user_id=str(bout.fighter_b_user_id),
        event_datetime_utc=bout.event_datetime_utc,
        finish_after_utc=bout.finish_after_utc,
        cancel_after_utc=bout.cancel_after_utc,
        show_a_drops=bout.show_a_drops,
        show_b_drops=bout.show_b_drops,
        bonus_a_drops=bout.bonus_a_drops,
        bonus_b_drops=bout.bonus_b_drops,
        bout_status=bout.status,
        winner=bout.winner,
        escrows=[
            BoutEscrowSummary(
                escrow_id=str(escrow.id),
                escrow_kind=escrow.kind,
                escrow_status=escrow.status,
                owner_address=escrow.owner_address,
                destination_address=escrow.destination_address,
                amount_drops=escrow.amount_drops,
                offer_sequence=escrow.offer_sequence,
                create_tx_hash=escrow.create_tx_hash,
                close_tx_hash=escrow.close_tx_hash,
            )
            for escrow in escrows
        ],
    )
