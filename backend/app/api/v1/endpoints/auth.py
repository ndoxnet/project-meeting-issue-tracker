# Concept by MrHan (08974747477)
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.context import RequestContext, get_request_context
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import Message
from app.schemas.user import UserResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse, operation_id="auth_login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
) -> TokenResponse:
    user, token, expires_in = await auth_service.authenticate(
        session, identifier=payload.username, password=payload.password, ctx=ctx
    )
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=Message, operation_id="auth_logout")
async def logout(
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    user: User = Depends(get_current_active_user),
) -> Message:
    # No server-side revocation in the MVP — the client must discard the token.
    await auth_service.record_logout(session, user=user, ctx=ctx)
    return Message(message="Logged out. Discard the access token on the client.")


@router.get("/me", response_model=UserResponse, operation_id="auth_get_current_user")
async def me(user: User = Depends(get_current_active_user)) -> UserResponse:
    return UserResponse.model_validate(user)
