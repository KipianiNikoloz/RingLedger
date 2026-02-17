from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> RegisterResponse:
    service = AuthService(session)
    try:
        user = service.register_user(email=payload.email, password=payload.password, role=payload.role)
    except ValueError as exc:
        if str(exc) == "email_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists."
            ) from exc
        raise
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create account.") from exc

    return RegisterResponse(user_id=str(user.id), email=user.email, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    service = AuthService(session)
    user = service.authenticate_user(email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    token = service.issue_access_token(user_id=user.id, email=user.email, role=user.role)
    return TokenResponse(access_token=token)
