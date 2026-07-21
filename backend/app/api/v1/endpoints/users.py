# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin
from app.api.deps.context import RequestContext, get_request_context
from app.db.session import get_db
from app.models.user import User
from app.repositories import user as user_repo
from app.schemas.common import Message, Page, PageMeta
from app.schemas.user import (
    PasswordResetRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services import user as user_service

router = APIRouter()


def _page_meta(page: int, page_size: int, total: int) -> PageMeta:
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PageMeta(page=page, page_size=page_size, total=total, pages=pages)


@router.get("", response_model=Page[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None, max_length=150),
    is_active: bool | None = Query(None),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Page[UserResponse]:
    items, total = await user_repo.list_users(
        session,
        offset=(page - 1) * page_size,
        limit=page_size,
        search=search,
        is_active=is_active,
    )
    return Page[UserResponse](
        items=[UserResponse.model_validate(u) for u in items],
        meta=_page_meta(page, page_size, total),
    )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> UserResponse:
    user = await user_service.create_user(session, data=payload, actor=actor, ctx=ctx)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    from app.core.errors import NotFoundError

    user = await user_repo.get_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> UserResponse:
    user = await user_service.update_user(
        session, user_id=user_id, data=payload, actor=actor, ctx=ctx
    )
    return UserResponse.model_validate(user)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> UserResponse:
    user = await user_service.set_active(
        session, user_id=user_id, active=True, actor=actor, ctx=ctx
    )
    return UserResponse.model_validate(user)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> UserResponse:
    user = await user_service.set_active(
        session, user_id=user_id, active=False, actor=actor, ctx=ctx
    )
    return UserResponse.model_validate(user)


@router.post("/{user_id}/reset-password", response_model=Message)
async def reset_password(
    user_id: uuid.UUID,
    payload: PasswordResetRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> Message:
    await user_service.reset_password(
        session, user_id=user_id, new_password=payload.new_password, actor=actor, ctx=ctx
    )
    return Message(message="Password has been reset.")
