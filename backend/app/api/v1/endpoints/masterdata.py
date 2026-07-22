# Concept by MrHan (08974747477)
"""Concrete named routers + meeting occurrences + app settings."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin, require_any, require_editor
from app.api.deps.context import RequestContext, get_request_context
from app.api.v1.endpoints._named import make_named_router
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.category import Category
from app.models.meeting import Meeting
from app.models.responsible_party import ResponsibleParty
from app.models.user import User
from app.repositories import masterdata as repo
from app.schemas.common import Page, PageMeta
from app.schemas.masterdata import (
    AppSettingResponse,
    AppSettingUpdate,
    MeetingOccurrenceCreate,
    MeetingOccurrenceResponse,
    MeetingOccurrenceUpdate,
)
from app.services import masterdata as svc

# Named master data (read: any role; write: admin).
categories_router = make_named_router(Category, "category")
responsible_parties_router = make_named_router(ResponsibleParty, "responsible_party")
meetings_router = make_named_router(Meeting, "meeting")


# ---- Meeting occurrences ----
occurrences_router = APIRouter()


def _page_meta(page: int, page_size: int, total: int) -> PageMeta:
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PageMeta(page=page, page_size=page_size, total=total, pages=pages)


@occurrences_router.get("", response_model=Page[MeetingOccurrenceResponse])
async def list_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    meeting_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> Page[MeetingOccurrenceResponse]:
    items, total = await repo.list_occurrences(
        session, offset=(page - 1) * page_size, limit=page_size, meeting_id=meeting_id
    )
    return Page[MeetingOccurrenceResponse](
        items=[MeetingOccurrenceResponse.model_validate(o) for o in items],
        meta=_page_meta(page, page_size, total),
    )


@occurrences_router.post("", response_model=MeetingOccurrenceResponse, status_code=201)
async def create_occurrence(
    payload: MeetingOccurrenceCreate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),  # editors may record occurrences
) -> MeetingOccurrenceResponse:
    occ = await svc.create_occurrence(session, data=payload, actor=actor, ctx=ctx)
    return MeetingOccurrenceResponse.model_validate(occ)


@occurrences_router.get("/{occ_id}", response_model=MeetingOccurrenceResponse)
async def get_occurrence(
    occ_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> MeetingOccurrenceResponse:
    occ = await repo.get_occurrence(session, occ_id)
    if occ is None:
        raise NotFoundError("Meeting occurrence not found")
    return MeetingOccurrenceResponse.model_validate(occ)


@occurrences_router.patch("/{occ_id}", response_model=MeetingOccurrenceResponse)
async def update_occurrence(
    occ_id: uuid.UUID,
    payload: MeetingOccurrenceUpdate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> MeetingOccurrenceResponse:
    occ = await svc.update_occurrence(session, occ_id=occ_id, data=payload, actor=actor, ctx=ctx)
    return MeetingOccurrenceResponse.model_validate(occ)


# ---- App settings ----
settings_router = APIRouter()


@settings_router.get("", response_model=list[AppSettingResponse])
async def list_settings(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[AppSettingResponse]:
    rows = await repo.list_settings(session)
    return [AppSettingResponse.model_validate(r) for r in rows]


@settings_router.get("/{key}", response_model=AppSettingResponse)
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> AppSettingResponse:
    setting = await repo.get_setting(session, key)
    if setting is None:
        raise NotFoundError("Setting not found")
    return AppSettingResponse.model_validate(setting)


@settings_router.patch("/{key}", response_model=AppSettingResponse)
async def update_setting(
    key: str,
    payload: AppSettingUpdate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> AppSettingResponse:
    setting = await svc.update_setting(session, key=key, value=payload.value, actor=actor, ctx=ctx)
    return AppSettingResponse.model_validate(setting)
