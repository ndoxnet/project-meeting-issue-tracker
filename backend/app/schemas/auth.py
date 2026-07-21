# Concept by MrHan (08974747477)
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    # `username` accepts either a username or an email address.
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
