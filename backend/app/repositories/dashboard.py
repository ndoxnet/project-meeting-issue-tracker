# Concept by MrHan (08974747477)
"""Dashboard aggregate queries. Archived issues are excluded everywhere.

Overdue/stagnant/due-this-week are computed against the local date (ADR-007).
The opened-vs-closed monthly trend is bucketed in Python for cross-dialect
portability (no strftime/to_char)."""

from __future__ import annotations

from collections import OrderedDict
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timezone import due_this_week_bounds, local_today
from app.models.category import Category
from app.models.enums import IssueStatus
from app.models.issue import Issue
from app.models.responsible_party import ResponsibleParty
from app.repositories.issue import _overdue_condition, _stagnant_condition

_ACTIVE = Issue.archived_at.is_(None)
_NOT_CLOSED = Issue.status != IssueStatus.CLOSED.value


async def _count(session: AsyncSession, *conds) -> int:
    stmt = select(func.count()).select_from(Issue)
    for c in conds:
        stmt = stmt.where(c)
    return int((await session.execute(stmt)).scalar_one())


def _month_start(today: date) -> date:
    return today.replace(day=1)


async def summary(session: AsyncSession, *, stagnant_days: int) -> dict[str, int]:
    today = local_today()
    week_start, week_end = due_this_week_bounds(today)
    month_start = _month_start(today)

    return {
        "open_count": await _count(session, _ACTIVE, Issue.status == IssueStatus.OPEN.value),
        "in_progress_count": await _count(
            session, _ACTIVE, Issue.status == IssueStatus.IN_PROGRESS.value
        ),
        "pending_count": await _count(session, _ACTIVE, Issue.status == IssueStatus.PENDING.value),
        "reopened_count": await _count(
            session, _ACTIVE, Issue.status == IssueStatus.REOPENED.value
        ),
        "overdue_count": await _count(session, _overdue_condition(today)),
        "stagnant_count": await _count(session, _stagnant_condition(stagnant_days, today)),
        "due_this_week_count": await _count(
            session,
            _ACTIVE,
            _NOT_CLOSED,
            Issue.due_date.is_not(None),
            Issue.due_date >= week_start,
            Issue.due_date <= week_end,
        ),
        "closed_this_month_count": await _count(
            session,
            Issue.status == IssueStatus.CLOSED.value,
            Issue.closed_date.is_not(None),
            Issue.closed_date >= month_start,
        ),
        "total_active_count": await _count(session, _ACTIVE, _NOT_CLOSED),
    }


async def overdue_issues(session: AsyncSession, *, limit: int = 50) -> list[Issue]:
    today = local_today()
    stmt = (
        select(Issue).where(_overdue_condition(today)).order_by(Issue.due_date.asc()).limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def stagnant_issues(
    session: AsyncSession, *, stagnant_days: int, limit: int = 50
) -> list[Issue]:
    today = local_today()
    stmt = (
        select(Issue)
        .where(_stagnant_condition(stagnant_days, today))
        .order_by(Issue.last_update_at.asc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def due_this_week_issues(session: AsyncSession, *, limit: int = 50) -> list[Issue]:
    today = local_today()
    week_start, week_end = due_this_week_bounds(today)
    stmt = (
        select(Issue)
        .where(
            _ACTIVE,
            _NOT_CLOSED,
            Issue.due_date.is_not(None),
            Issue.due_date >= week_start,
            Issue.due_date <= week_end,
        )
        .order_by(Issue.due_date.asc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def recently_updated_issues(session: AsyncSession, *, limit: int = 10) -> list[Issue]:
    stmt = (
        select(Issue)
        .where(_ACTIVE, Issue.last_update_at.is_not(None))
        .order_by(Issue.last_update_at.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def count_by_category(session: AsyncSession) -> list[tuple[str, int]]:
    stmt = (
        select(Category.name, func.count(Issue.id))
        .join(Category, Category.id == Issue.category_id)
        .where(_ACTIVE)
        .group_by(Category.name)
        .order_by(func.count(Issue.id).desc())
    )
    return [(name, int(c)) for name, c in (await session.execute(stmt)).all()]


async def count_by_responsible_party(session: AsyncSession) -> list[tuple[str, int]]:
    stmt = (
        select(ResponsibleParty.name, func.count(Issue.id))
        .join(ResponsibleParty, ResponsibleParty.id == Issue.responsible_party_id)
        .where(_ACTIVE)
        .group_by(ResponsibleParty.name)
        .order_by(func.count(Issue.id).desc())
    )
    return [(name, int(c)) for name, c in (await session.execute(stmt)).all()]


def _month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _month_range(today: date, months: int) -> list[str]:
    keys: list[str] = []
    y, m = today.year, today.month
    for _ in range(months):
        keys.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(keys))


async def opened_vs_closed(session: AsyncSession, *, months: int) -> list[tuple[str, int, int]]:
    """Opened (by raised_date) vs closed (by closed_date) per month, portable."""
    today = local_today()
    keys = _month_range(today, months)
    earliest = date(int(keys[0][:4]), int(keys[0][5:7]), 1)

    opened: OrderedDict[str, int] = OrderedDict((k, 0) for k in keys)
    closed: OrderedDict[str, int] = OrderedDict((k, 0) for k in keys)

    raised_rows = (
        await session.execute(select(Issue.raised_date).where(Issue.raised_date >= earliest))
    ).scalars()
    for d in raised_rows:
        k = _month_key(d)
        if k in opened:
            opened[k] += 1

    closed_rows = (
        await session.execute(
            select(Issue.closed_date).where(
                and_(Issue.closed_date.is_not(None), Issue.closed_date >= earliest)
            )
        )
    ).scalars()
    for cd in closed_rows:
        if cd is None:
            continue
        k = _month_key(cd)
        if k in closed:
            closed[k] += 1

    return [(k, opened[k], closed[k]) for k in keys]
