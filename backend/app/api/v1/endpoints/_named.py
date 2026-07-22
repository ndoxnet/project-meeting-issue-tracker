# Concept by MrHan (08974747477)
"""Factory for the three structurally-identical named master-data routers
(categories, responsible parties, meetings). Read = any role; write = admin."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin, require_any
from app.api.deps.context import RequestContext, get_request_context
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.repositories import masterdata as repo
from app.schemas.common import Page, PageMeta
from app.schemas.masterdata import NamedCreate, NamedResponse, NamedUpdate
from app.services import masterdata as svc


def _page_meta(page: int, page_size: int, total: int) -> PageMeta:
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PageMeta(page=page, page_size=page_size, total=total, pages=pages)


def make_named_router(model: type, entity_type: str) -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=Page[NamedResponse])
    async def list_items(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=200),
        is_active: bool | None = Query(None),
        search: str | None = Query(None, max_length=150),
        session: AsyncSession = Depends(get_db),
        _: User = Depends(require_any),
    ) -> Page[NamedResponse]:
        items, total = await repo.list_named(
            session,
            model,
            offset=(page - 1) * page_size,
            limit=page_size,
            is_active=is_active,
            search=search,
        )
        return Page[NamedResponse](
            items=[NamedResponse.model_validate(i) for i in items],
            meta=_page_meta(page, page_size, total),
        )

    @router.post("", response_model=NamedResponse, status_code=201)
    async def create_item(
        payload: NamedCreate,
        session: AsyncSession = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        actor: User = Depends(require_admin),
    ) -> NamedResponse:
        obj = await svc.create_named(
            session, model, entity_type=entity_type, data=payload, actor=actor, ctx=ctx
        )
        return NamedResponse.model_validate(obj)

    @router.get("/{item_id}", response_model=NamedResponse)
    async def get_item(
        item_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        _: User = Depends(require_any),
    ) -> NamedResponse:
        obj = await repo.get_named(session, model, item_id)
        if obj is None:
            raise NotFoundError(f"{entity_type} not found")
        return NamedResponse.model_validate(obj)

    @router.patch("/{item_id}", response_model=NamedResponse)
    async def update_item(
        item_id: uuid.UUID,
        payload: NamedUpdate,
        session: AsyncSession = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        actor: User = Depends(require_admin),
    ) -> NamedResponse:
        obj = await svc.update_named(
            session,
            model,
            entity_type=entity_type,
            obj_id=item_id,
            data=payload,
            actor=actor,
            ctx=ctx,
        )
        return NamedResponse.model_validate(obj)

    @router.post("/{item_id}/activate", response_model=NamedResponse)
    async def activate_item(
        item_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        actor: User = Depends(require_admin),
    ) -> NamedResponse:
        obj = await svc.set_named_active(
            session,
            model,
            entity_type=entity_type,
            obj_id=item_id,
            active=True,
            actor=actor,
            ctx=ctx,
        )
        return NamedResponse.model_validate(obj)

    @router.post("/{item_id}/deactivate", response_model=NamedResponse)
    async def deactivate_item(
        item_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        actor: User = Depends(require_admin),
    ) -> NamedResponse:
        obj = await svc.set_named_active(
            session,
            model,
            entity_type=entity_type,
            obj_id=item_id,
            active=False,
            actor=actor,
            ctx=ctx,
        )
        return NamedResponse.model_validate(obj)

    return router
