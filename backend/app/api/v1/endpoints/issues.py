# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin, require_any, require_editor
from app.api.deps.context import RequestContext, get_request_context
from app.core.config import get_settings
from app.db.session import get_db
from app.models.issue import Issue
from app.models.user import User
from app.repositories import issue as issue_repo
from app.schemas.common import Page, PageMeta
from app.schemas.issue import (
    DuplicateWarning,
    IssueArchiveRequest,
    IssueCloseRequest,
    IssueCreate,
    IssueCreateResponse,
    IssueDetailResponse,
    IssueListItem,
    IssueMetadataUpdate,
    IssueReopenRequest,
    IssueRestoreRequest,
    IssueStatusChangeRequest,
)
from app.services import issue as issue_service
from app.services.issue_view import map_detail, map_list_item

router = APIRouter()


def _page_meta(page: int, page_size: int, total: int) -> PageMeta:
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PageMeta(page=page, page_size=page_size, total=total, pages=pages)


async def _detail(session: AsyncSession, issue: Issue) -> IssueDetailResponse:
    cats, rps = await issue_repo.get_names_for(session, [issue])
    return map_detail(
        issue,
        category_name=cats.get(issue.category_id),
        responsible_party_name=(
            rps.get(issue.responsible_party_id) if issue.responsible_party_id else None
        ),
    )


@router.get("", response_model=Page[IssueListItem])
async def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None, max_length=200),
    issue_code: str | None = Query(None, max_length=30),
    status: list[str] | None = Query(None),
    priority: str | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    responsible_party_id: uuid.UUID | None = Query(None),
    pic_user_id: uuid.UUID | None = Query(None),
    pic_name: str | None = Query(None, max_length=150),
    meeting_id: uuid.UUID | None = Query(None),
    meeting_occurrence_id: uuid.UUID | None = Query(None),
    raised_date_from: date | None = Query(None),
    raised_date_to: date | None = Query(None),
    due_date_from: date | None = Query(None),
    due_date_to: date | None = Query(None),
    updated_from: datetime | None = Query(None),
    updated_to: datetime | None = Query(None),
    overdue: bool | None = Query(None),
    stagnant: bool | None = Query(None),
    include_archived: bool = Query(False),
    sort_by: str | None = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> Page[IssueListItem]:
    settings = get_settings()
    f = issue_repo.IssueListFilters(
        search=search,
        issue_code=issue_code,
        statuses=status or [],
        priority=priority,
        category_id=category_id,
        responsible_party_id=responsible_party_id,
        pic_user_id=pic_user_id,
        pic_name=pic_name,
        meeting_id=meeting_id,
        meeting_occurrence_id=meeting_occurrence_id,
        raised_date_from=raised_date_from,
        raised_date_to=raised_date_to,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        updated_from=updated_from,
        updated_to=updated_to,
        overdue=overdue,
        stagnant=stagnant,
        include_archived=include_archived,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    rows, total = await issue_repo.list_issues(
        session,
        f=f,
        offset=(page - 1) * page_size,
        limit=page_size,
        stagnant_days=settings.STAGNANT_DAYS,
    )
    cats, rps = await issue_repo.get_names_for(session, rows)
    items = [
        map_list_item(
            i,
            category_name=cats.get(i.category_id),
            responsible_party_name=(
                rps.get(i.responsible_party_id) if i.responsible_party_id else None
            ),
        )
        for i in rows
    ]
    return Page[IssueListItem](items=items, meta=_page_meta(page, page_size, total))


@router.post("", response_model=IssueCreateResponse, status_code=201)
async def create_issue(
    payload: IssueCreate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueCreateResponse:
    issue, dupes = await issue_service.create_issue(session, data=payload, actor=actor, ctx=ctx)
    warnings = [
        DuplicateWarning(issue_id=d.id, issue_code=d.issue_code, title=d.title) for d in dupes
    ]
    return IssueCreateResponse(issue=await _detail(session, issue), warnings=warnings)


@router.get("/{issue_id}", response_model=IssueDetailResponse)
async def get_issue(
    issue_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> IssueDetailResponse:
    issue = await issue_service.get_issue_or_404(session, issue_id)
    return await _detail(session, issue)


@router.patch("/{issue_id}", response_model=IssueDetailResponse)
async def update_issue(
    issue_id: uuid.UUID,
    payload: IssueMetadataUpdate,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueDetailResponse:
    issue = await issue_service.update_metadata(
        session, issue_id=issue_id, data=payload, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)


@router.post("/{issue_id}/status", response_model=IssueDetailResponse)
async def change_status(
    issue_id: uuid.UUID,
    payload: IssueStatusChangeRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueDetailResponse:
    issue = await issue_service.change_status(
        session, issue_id=issue_id, data=payload, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)


@router.post("/{issue_id}/close", response_model=IssueDetailResponse)
async def close_issue(
    issue_id: uuid.UUID,
    payload: IssueCloseRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueDetailResponse:
    issue = await issue_service.close_issue(
        session, issue_id=issue_id, data=payload, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)


@router.post("/{issue_id}/reopen", response_model=IssueDetailResponse)
async def reopen_issue(
    issue_id: uuid.UUID,
    payload: IssueReopenRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> IssueDetailResponse:
    issue = await issue_service.reopen_issue(
        session, issue_id=issue_id, data=payload, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)


@router.post("/{issue_id}/archive", response_model=IssueDetailResponse)
async def archive_issue(
    issue_id: uuid.UUID,
    payload: IssueArchiveRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> IssueDetailResponse:
    issue = await issue_service.archive_issue(
        session, issue_id=issue_id, reason=payload.reason, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)


@router.post("/{issue_id}/restore", response_model=IssueDetailResponse)
async def restore_issue(
    issue_id: uuid.UUID,
    payload: IssueRestoreRequest,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> IssueDetailResponse:
    issue = await issue_service.restore_issue(
        session, issue_id=issue_id, reason=payload.reason, actor=actor, ctx=ctx
    )
    return await _detail(session, issue)
