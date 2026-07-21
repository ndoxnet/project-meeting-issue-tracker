# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserRole


def _norm_username(v: str) -> str:
    return v.strip().lower()


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    role: UserRole

    @field_validator("username")
    @classmethod
    def _username(cls, v: str) -> str:
        return _norm_username(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return v.strip().lower()


class UserCreate(UserBase):
    # Password policy is enforced in the service (length + not-equal-to-identity).
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    role: UserRole | None = None

    @field_validator("email")
    @classmethod
    def _email(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v


class PasswordResetRequest(BaseModel):
    # Admin supplies the new password explicitly (no email workflow in the MVP).
    new_password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    username: str
    role: UserRole
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    # NOTE: password_hash is deliberately absent — it must never be serialized.
