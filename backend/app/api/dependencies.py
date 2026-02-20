from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings
from app.core.security import decode_access_token
from app.models.enums import UserRole


@dataclass(frozen=True)
class RequestActor:
    user_id: uuid.UUID
    email: str
    role: UserRole


def get_current_actor(authorization: str | None = Header(default=None, alias="Authorization")) -> RequestActor:
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is required.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use Bearer token format.",
        )

    try:
        payload = decode_access_token(token.strip(), secret_key=settings.jwt_secret)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token."
        ) from exc

    subject = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")
    if not isinstance(subject, str) or not isinstance(email, str) or not isinstance(role, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token claims.")

    try:
        user_id = uuid.UUID(subject)
        role_enum = UserRole(role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token claims.") from exc

    return RequestActor(user_id=user_id, email=email, role=role_enum)


def require_role(required_role: UserRole):
    def dependency(actor: Annotated[RequestActor, Depends(get_current_actor)]) -> RequestActor:
        if actor.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role for this operation.")
        return actor

    return dependency
