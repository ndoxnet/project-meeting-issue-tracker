# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_any
from app.api.deps.context import RequestContext, get_request_context
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories import issue as issue_repo
from app.services import report as report_service

router = APIRouter()


@router.get("/issues.csv")
async def export_issues_csv(
    search: str | None = Query(None, max_length=200),
    status: list[str] | None = Query(None),
    priority: str | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    responsible_party_id: uuid.UUID | None = Query(None),
    pic_user_id: uuid.UUID | None = Query(None),
    raised_date_from: date | None = Query(None),
    raised_date_to: date | None = Query(None),
    due_date_from: date | None = Query(None),
    due_date_to: date | None = Query(None),
    overdue: bool | None = Query(None),
    stagnant: bool | None = Query(None),
    include_archived: bool = Query(False),
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_any),
) -> Response:
    f = issue_repo.IssueListFilters(
        search=search,
        statuses=status or [],
        priority=priority,
        category_id=category_id,
        responsible_party_id=responsible_party_id,
        pic_user_id=pic_user_id,
        raised_date_from=raised_date_from,
        raised_date_to=raised_date_to,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        overdue=overdue,
        stagnant=stagnant,
        include_archived=include_archived,
    )
    body = await report_service.export_issues_csv(
        session, f=f, actor=actor, ctx=ctx, stagnant_days=get_settings().STAGNANT_DAYS
    )
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="issues.csv"'},
    )
