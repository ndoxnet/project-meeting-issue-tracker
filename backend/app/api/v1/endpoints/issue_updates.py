# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin, require_any, require_editor
from app.api.deps.context import RequestContext, get_request_context
from app.core.errors import DomainError
from app.db.session import get_db
from app.models.user import User
from app.repositories import issue as issue_repo
from app.schemas.issue import (
    IssueUpdateCreate,
    IssueUpdateResponse,
    IssueUpdateVoidRequest,
    VoidResponse,
)
from app.services import issue as issue_service
from app.services import issue_update as update_service

router = APIRouter()


@router.get("/{issue_id}/updates", response_model=list[IssueUpdateResponse])
async def list_updates(
    issue_id: uuid.UUID,
    order: str = Query("asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[IssueUpdateResponse]:
    await issue_service.get_issue_or_404(session, issue_id)
    rows = await issue_repo.list_updates(session, issue_id, ascending=(order == "asc"))
    return [IssueUpdateResponse.model_validate(r) for r in rows]


@router.post("/{issue_id}/updates", response_model=IssueUpdateResponse, status_code=201)
async def create_update(
    issue_id: uuid.UUID,
    payload: IssueUpdateCreate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueUpdateResponse:
    upd = await update_service.create_follow_up(
        session, issue_id=issue_id, data=payload, actor=actor, ctx=ctx
    )
    return IssueUpdateResponse.model_validate(upd)


@router.get("/{issue_id}/updates/{update_id}", response_model=IssueUpdateResponse)
async def get_update(
    issue_id: uuid.UUID,
    update_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> IssueUpdateResponse:
    upd = await issue_repo.get_update(session, update_id)
    if upd is None or upd.issue_id != issue_id:
        raise DomainError("ISSUE_UPDATE_NOT_FOUND", "Issue update not found", http_status=404)
    return IssueUpdateResponse.model_validate(upd)


@router.post("/{issue_id}/updates/{update_id}/void", response_model=VoidResponse)
async def void_update(
    issue_id: uuid.UUID,
    update_id: uuid.UUID,
    payload: IssueUpdateVoidRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> VoidResponse:
    upd, warnings = await update_service.void_update(
        session,
        issue_id=issue_id,
        update_id=update_id,
        void_reason=payload.void_reason,
        actor=actor,
        ctx=ctx,
    )
    return VoidResponse(update=IssueUpdateResponse.model_validate(upd), warnings=warnings)
