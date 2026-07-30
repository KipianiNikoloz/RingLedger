from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import RequestActor, require_role
from app.db.session import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.models.enums import UserRole
from app.schemas.auth import AdminUserCreateRequest, RegisterResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def create_privileged_user(
    payload: AdminUserCreateRequest,
    _actor: RequestActor = Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_session),
) -> RegisterResponse:
    uow = SqlAlchemyUnitOfWork(session=session)
    try:
        user = AuthService(session).register_user(email=payload.email, password=payload.password, role=payload.role)
        uow.commit()
    except ValueError as exc:
        uow.rollback()
        if str(exc) == "email_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists."
            ) from exc
        raise
    except IntegrityError as exc:
        uow.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create account.") from exc
    except Exception:
        uow.rollback()
        raise
    return RegisterResponse(user_id=str(user.id), email=user.email, role=user.role)
