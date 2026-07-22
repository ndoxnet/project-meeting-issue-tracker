# Concept by MrHan (08974747477)
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_any
from app.core.config import get_settings
from app.db.session import get_db
from app.models.issue import Issue
from app.models.user import User
from app.repositories import dashboard as dash_repo
from app.repositories import issue as issue_repo
from app.schemas.dashboard import CountByLabel, DashboardSummary, MonthlyTrendPoint
from app.schemas.issue import IssueListItem
from app.services.issue_view import map_list_item

router = APIRouter()


async def _items(session: AsyncSession, rows: list[Issue]) -> list[IssueListItem]:
    cats, rps = await issue_repo.get_names_for(session, rows)
    return [
        map_list_item(
            i,
            category_name=cats.get(i.category_id),
            responsible_party_name=(
                rps.get(i.responsible_party_id) if i.responsible_party_id else None
            ),
        )
        for i in rows
    ]


@router.get("/summary", response_model=DashboardSummary)
async def summary(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> DashboardSummary:
    data = await dash_repo.summary(session, stagnant_days=get_settings().STAGNANT_DAYS)
    return DashboardSummary(**data)


@router.get("/overdue", response_model=list[IssueListItem])
async def overdue(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[IssueListItem]:
    return await _items(session, await dash_repo.overdue_issues(session, limit=limit))


@router.get("/stagnant", response_model=list[IssueListItem])
async def stagnant(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[IssueListItem]:
    rows = await dash_repo.stagnant_issues(
        session, stagnant_days=get_settings().STAGNANT_DAYS, limit=limit
    )
    return await _items(session, rows)


@router.get("/due-this-week", response_model=list[IssueListItem])
async def due_this_week(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[IssueListItem]:
    return await _items(session, await dash_repo.due_this_week_issues(session, limit=limit))


@router.get("/recently-updated", response_model=list[IssueListItem])
async def recently_updated(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[IssueListItem]:
    return await _items(session, await dash_repo.recently_updated_issues(session, limit=limit))


@router.get("/by-category", response_model=list[CountByLabel])
async def by_category(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[CountByLabel]:
    return [CountByLabel(label=n, count=c) for n, c in await dash_repo.count_by_category(session)]


@router.get("/by-responsible-party", response_model=list[CountByLabel])
async def by_responsible_party(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[CountByLabel]:
    return [
        CountByLabel(label=n, count=c)
        for n, c in await dash_repo.count_by_responsible_party(session)
    ]


@router.get("/opened-vs-closed", response_model=list[MonthlyTrendPoint])
async def opened_vs_closed(
    months: int = Query(6, ge=1, le=24),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[MonthlyTrendPoint]:
    return [
        MonthlyTrendPoint(month=m, opened=o, closed=c)
        for m, o, c in await dash_repo.opened_vs_closed(session, months=months)
    ]
