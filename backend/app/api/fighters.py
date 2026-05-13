from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.models.enums import UserRole
from app.schemas.fighter import FighterProfileResponse, FighterProfileUpsertRequest
from app.services.fighter_profile_service import FighterProfileService

router = APIRouter(prefix="/fighters", tags=["fighters"])


@router.put("/me", response_model=FighterProfileResponse)
def upsert_my_fighter_profile(
    payload: FighterProfileUpsertRequest,
    actor: RequestActor = Depends(require_role(UserRole.FIGHTER)),
    session: Session = Depends(get_session),
) -> FighterProfileResponse:
    uow = SqlAlchemyUnitOfWork(session=session)
    service = FighterProfileService(session=session)
    try:
        profile = service.upsert_profile(
            user_id=actor.user_id,
            display_name=payload.display_name,
            xrpl_address=payload.xrpl_address,
        )
        uow.commit()
    except ValueError as exc:
        uow.rollback()
        if str(exc) == "xrpl_address_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="XRPL address is already assigned to another fighter profile.",
            ) from exc
        raise
    except IntegrityError as exc:
        uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not persist fighter profile.",
        ) from exc
    except Exception:
        uow.rollback()
        raise

    return FighterProfileResponse(
        profile_id=str(profile.id),
        user_id=str(profile.user_id),
        display_name=profile.display_name,
        xrpl_address=profile.xrpl_address,
    )
