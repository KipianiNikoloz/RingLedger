from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User


@dataclass
class AuthService:
    session: Session

    def register_user(self, *, email: str, password: str, role: UserRole) -> User:
        normalized_email = email.strip().lower()
        existing = self.session.scalar(select(User).where(User.email == normalized_email))
        if existing is not None:
            raise ValueError("email_already_exists")

        user = User(email=normalized_email, password_hash=hash_password(password), role=role)
        self.session.add(user)
        self.session.flush()
        return user

    def authenticate_user(self, *, email: str, password: str) -> User | None:
        normalized_email = email.strip().lower()
        user = self.session.scalar(select(User).where(User.email == normalized_email))
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def issue_access_token(*, user_id: uuid.UUID, email: str, role: UserRole) -> str:
        return create_access_token(
            subject=str(user_id),
            email=email,
            role=role.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
