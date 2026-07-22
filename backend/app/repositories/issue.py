# Concept by MrHan (08974747477)
"""Issue data access: filtered/sorted/paginated list, detail with names,
per-year counter, duplicate check, and follow-up updates."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timezone import local_today, now_utc
from app.models.category import Category
from app.models.enums import IssueStatus
from app.models.issue import Issue, IssueUpdate
from app.models.issue_counter import IssueCounter
from app.models.meeting import MeetingOccurrence
from app.models.responsible_party import ResponsibleParty

# Allow-list of sortable columns (never accept a raw column name from a request).
SORTABLE = {
    "issue_code": Issue.issue_code,
    "raised_date": Issue.raised_date,
    "due_date": Issue.due_date,
    "last_update_at": Issue.last_update_at,
    "updated_at": Issue.updated_at,
    "priority": Issue.priority,
    "status": Issue.status,
}

# Priority ordering for the default "critical first" sort.
_PRIORITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


@dataclass
class IssueListFilters:
    search: str | None = None
    issue_code: str | None = None
    statuses: list[str] = field(default_factory=list)
    priority: str | None = None
    category_id: uuid.UUID | None = None
    responsible_party_id: uuid.UUID | None = None
    pic_user_id: uuid.UUID | None = None
    pic_name: str | None = None
    meeting_id: uuid.UUID | None = None
    meeting_occurrence_id: uuid.UUID | None = None
    raised_date_from: date | None = None
    raised_date_to: date | None = None
    due_date_from: date | None = None
    due_date_to: date | None = None
    updated_from: datetime | None = None
    updated_to: datetime | None = None
    overdue: bool | None = None
    stagnant: bool | None = None
    include_archived: bool = False
    sort_by: str | None = None
    sort_order: str = "asc"


async def get_issue(
    session: AsyncSession, issue_id: uuid.UUID, *, for_update: bool = False
) -> Issue | None:
    """Fetch an issue. With for_update=True, take a row lock (SELECT ... FOR
    UPDATE) so concurrent state transitions serialize (ADR-016). On SQLite the
    lock clause is ignored; the DB write-lock still serializes writers."""
    if for_update:
        stmt = select(Issue).where(Issue.id == issue_id).with_for_update()
        return (await session.execute(stmt)).scalar_one_or_none()
    return await session.get(Issue, issue_id)


def _apply_filters(stmt: Select, f: IssueListFilters, stagnant_days: int) -> Select:
    today = local_today()

    if not f.include_archived:
        stmt = stmt.where(Issue.archived_at.is_(None))
    if f.issue_code:
        stmt = stmt.where(Issue.issue_code == f.issue_code.strip())
    if f.search:
        like = f"%{f.search.strip()}%"
        stmt = stmt.where(
            or_(
                Issue.issue_code.ilike(like),
                Issue.title.ilike(like),
                Issue.description.ilike(like),
                Issue.pic_name.ilike(like),
                Issue.next_action.ilike(like),
            )
        )
    if f.statuses:
        stmt = stmt.where(Issue.status.in_(f.statuses))
    if f.priority:
        stmt = stmt.where(Issue.priority == f.priority)
    if f.category_id:
        stmt = stmt.where(Issue.category_id == f.category_id)
    if f.responsible_party_id:
        stmt = stmt.where(Issue.responsible_party_id == f.responsible_party_id)
    if f.pic_user_id:
        stmt = stmt.where(Issue.pic_user_id == f.pic_user_id)
    if f.pic_name:
        stmt = stmt.where(Issue.pic_name.ilike(f"%{f.pic_name.strip()}%"))
    if f.meeting_occurrence_id:
        stmt = stmt.where(Issue.raised_in_meeting_occurrence_id == f.meeting_occurrence_id)
    if f.meeting_id:
        sub = select(MeetingOccurrence.id).where(MeetingOccurrence.meeting_id == f.meeting_id)
        stmt = stmt.where(Issue.raised_in_meeting_occurrence_id.in_(sub))
    if f.raised_date_from:
        stmt = stmt.where(Issue.raised_date >= f.raised_date_from)
    if f.raised_date_to:
        stmt = stmt.where(Issue.raised_date <= f.raised_date_to)
    if f.due_date_from:
        stmt = stmt.where(Issue.due_date >= f.due_date_from)
    if f.due_date_to:
        stmt = stmt.where(Issue.due_date <= f.due_date_to)
    if f.updated_from:
        stmt = stmt.where(Issue.updated_at >= f.updated_from)
    if f.updated_to:
        stmt = stmt.where(Issue.updated_at <= f.updated_to)
    if f.overdue:
        stmt = stmt.where(_overdue_condition(today))
    if f.stagnant:
        stmt = stmt.where(_stagnant_condition(stagnant_days, today))
    return stmt


def _overdue_condition(today: date):
    return and_(
        Issue.status != IssueStatus.CLOSED.value,
        Issue.archived_at.is_(None),
        Issue.due_date.is_not(None),
        Issue.due_date < today,
    )


def _stagnant_condition(stagnant_days: int, today: date):
    cutoff_dt = now_utc() - timedelta(days=stagnant_days)
    cutoff_date = today - timedelta(days=stagnant_days)
    return and_(
        Issue.status != IssueStatus.CLOSED.value,
        Issue.archived_at.is_(None),
        or_(
            and_(Issue.last_update_at.is_not(None), Issue.last_update_at < cutoff_dt),
            and_(Issue.last_update_at.is_(None), Issue.raised_date < cutoff_date),
        ),
    )


def _order_by(stmt: Select, f: IssueListFilters, today: date) -> Select:
    if f.sort_by and f.sort_by in SORTABLE:
        col = SORTABLE[f.sort_by]
        return stmt.order_by(col.asc() if f.sort_order == "asc" else col.desc())
    # Default (portable): critical first, overdue first, nearest due date (nulls
    # last), then most recently updated.
    prank = case(_PRIORITY_ORDER, value=Issue.priority, else_=99)
    overdue_first = case((_overdue_condition(today), 0), else_=1)
    return stmt.order_by(
        prank.asc(),
        overdue_first.asc(),
        Issue.due_date.is_(None).asc(),  # False (0) before True (1) => nulls last
        Issue.due_date.asc(),
        Issue.last_update_at.desc(),
    )


async def list_issues(
    session: AsyncSession,
    *,
    f: IssueListFilters,
    offset: int,
    limit: int,
    stagnant_days: int,
) -> tuple[list[Issue], int]:
    today = local_today()
    base = select(Issue)
    base = _apply_filters(base, f, stagnant_days)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    base = _order_by(base, f, today)
    rows = (await session.execute(base.offset(offset).limit(limit))).scalars().all()
    return list(rows), int(total)


async def get_names_for(
    session: AsyncSession, issues: list[Issue]
) -> tuple[dict[uuid.UUID, str], dict[uuid.UUID, str]]:
    """Batch-load category and responsible-party names (avoids N+1)."""
    cat_ids = {i.category_id for i in issues}
    rp_ids = {i.responsible_party_id for i in issues if i.responsible_party_id}
    cats: dict[uuid.UUID, str] = {}
    rps: dict[uuid.UUID, str] = {}
    if cat_ids:
        for c in (
            await session.execute(select(Category).where(Category.id.in_(cat_ids)))
        ).scalars():
            cats[c.id] = c.name
    if rp_ids:
        for r in (
            await session.execute(select(ResponsibleParty).where(ResponsibleParty.id.in_(rp_ids)))
        ).scalars():
            rps[r.id] = r.name
    return cats, rps


async def find_possible_duplicates(
    session: AsyncSession, *, title: str, category_id: uuid.UUID, limit: int = 5
) -> list[Issue]:
    """Simple duplicate heuristic: same category, not closed/archived, and title
    exact (case-insensitive) OR ILIKE-similar. No AI / fuzzy library."""
    norm = title.strip().lower()
    like = f"%{norm}%"
    stmt = (
        select(Issue)
        .where(
            Issue.category_id == category_id,
            Issue.archived_at.is_(None),
            Issue.status != IssueStatus.CLOSED.value,
            or_(func.lower(Issue.title) == norm, Issue.title.ilike(like)),
        )
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def next_issue_number(session: AsyncSession, year: int) -> int:
    """Atomically allocate the next per-year sequence number (ADR-011).

    Uses INSERT ... ON CONFLICT (year) DO UPDATE SET last_number = last_number + 1
    RETURNING last_number. This is concurrency-safe even for the FIRST issue of a
    year: a plain SELECT ... FOR UPDATE would lock nothing when the counter row
    does not yet exist, letting concurrent creators collide. The upsert serializes
    concurrent increments on the row (PostgreSQL) and returns a distinct number to
    each transaction. Portable to SQLite (>= 3.35, RETURNING) used in tests."""
    dialect = session.bind.dialect.name
    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as _pg_insert

        insert_fn: Any = _pg_insert
    else:
        from sqlalchemy.dialects.sqlite import insert as _sqlite_insert

        insert_fn = _sqlite_insert

    stmt = (
        insert_fn(IssueCounter)
        .values(year=year, last_number=1)
        .on_conflict_do_update(
            index_elements=[IssueCounter.year],
            set_={"last_number": IssueCounter.last_number + 1},
        )
        .returning(IssueCounter.last_number)
    )
    return int((await session.execute(stmt)).scalar_one())


# ---- issue updates ----
async def get_update(session: AsyncSession, update_id: uuid.UUID) -> IssueUpdate | None:
    return await session.get(IssueUpdate, update_id)


async def list_updates(
    session: AsyncSession, issue_id: uuid.UUID, *, ascending: bool = True
) -> list[IssueUpdate]:
    order = IssueUpdate.created_at.asc() if ascending else IssueUpdate.created_at.desc()
    rows = (
        (
            await session.execute(
                select(IssueUpdate).where(IssueUpdate.issue_id == issue_id).order_by(order)
            )
        )
        .scalars()
        .all()
    )
    return list(rows)
