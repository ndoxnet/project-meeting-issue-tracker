# Concept by MrHan (08974747477)
"""CSV export of the filtered issue register.

Reuses the issue-list filters. Enforces a hard row cap, escapes formula
injection, prepends a UTF-8 BOM (Excel-friendly), and audits the export (filters
+ row count only — never the CSV body). Internal fields are never exported."""

from __future__ import annotations

import csv
import io
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.errors import DomainError
from app.models.user import User
from app.repositories import issue as issue_repo
from app.services.audit import record_audit
from app.utils.csv_safe import sanitize_cell

EXPORT_MAX_ROWS = 10_000

COLUMNS = [
    "Issue Code",
    "Title",
    "Description",
    "Category",
    "Responsible Party",
    "Priority",
    "Status",
    "Raised Date",
    "PIC",
    "Due Date",
    "Next Action",
    "Last Update",
    "Last Update Date",
    "Closed Date",
    "Archived",
    "Created By",
    "Created At",
]


async def export_issues_csv(
    session: AsyncSession,
    *,
    f: issue_repo.IssueListFilters,
    actor: User,
    ctx: RequestContext,
    stagnant_days: int,
) -> bytes:
    rows, total = await issue_repo.list_issues(
        session, f=f, offset=0, limit=EXPORT_MAX_ROWS + 1, stagnant_days=stagnant_days
    )
    if total > EXPORT_MAX_ROWS:
        raise DomainError(
            "EXPORT_LIMIT_EXCEEDED",
            f"Export exceeds the maximum of {EXPORT_MAX_ROWS} rows; narrow the filters",
            http_status=409,
        )

    cats, rps = await issue_repo.get_names_for(session, rows)
    creators = await _usernames(session, {r.created_by for r in rows})

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(COLUMNS)
    for i in rows:
        writer.writerow(
            [
                sanitize_cell(i.issue_code),
                sanitize_cell(i.title),
                sanitize_cell(i.description),
                sanitize_cell(cats.get(i.category_id, "")),
                sanitize_cell(
                    rps.get(i.responsible_party_id, "") if i.responsible_party_id else ""
                ),
                sanitize_cell(i.priority),
                sanitize_cell(i.status),
                sanitize_cell(i.raised_date.isoformat()),
                sanitize_cell(i.pic_name or ""),
                sanitize_cell(i.due_date.isoformat() if i.due_date else ""),
                sanitize_cell(i.next_action or ""),
                sanitize_cell(i.last_update_summary or ""),
                sanitize_cell(i.last_update_at.isoformat() if i.last_update_at else ""),
                sanitize_cell(i.closed_date.isoformat() if i.closed_date else ""),
                sanitize_cell("yes" if i.archived_at is not None else "no"),
                sanitize_cell(creators.get(i.created_by, "")),
                sanitize_cell(i.created_at.isoformat() if i.created_at else ""),
            ]
        )

    record_audit(
        session,
        action="report.issue_csv_export",
        entity_type="report",
        entity_id=None,
        actor_user_id=actor.id,
        after={"row_count": len(rows), "filters": _filters_public(f)},
        ctx=ctx,
    )
    await session.commit()

    # UTF-8 BOM so Excel detects the encoding.
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


async def _usernames(session: AsyncSession, ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    ids = {i for i in ids if i}
    if not ids:
        return {}
    rows = (await session.execute(select(User).where(User.id.in_(ids)))).scalars()
    return {u.id: u.username for u in rows}


def _filters_public(f: issue_repo.IssueListFilters) -> dict:
    return {
        "search": f.search,
        "statuses": f.statuses,
        "priority": f.priority,
        "category_id": str(f.category_id) if f.category_id else None,
        "responsible_party_id": str(f.responsible_party_id) if f.responsible_party_id else None,
        "pic_user_id": str(f.pic_user_id) if f.pic_user_id else None,
        "overdue": f.overdue,
        "stagnant": f.stagnant,
        "include_archived": f.include_archived,
    }
