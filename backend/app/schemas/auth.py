from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AdminUserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole

    @field_validator("role")
    @classmethod
    def role_must_be_privileged(cls, value: UserRole) -> UserRole:
        if value not in {UserRole.PROMOTER, UserRole.MANAGEMENT, UserRole.ADMIN}:
            raise ValueError("role must be promoter, management, or admin")
        return value


class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
