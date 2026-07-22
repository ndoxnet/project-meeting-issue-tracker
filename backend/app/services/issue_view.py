# Concept by MrHan (08974747477)
"""Pure mappers that build response schemas with computed (not stored) fields:
days_open, days_since_last_update, is_overdue (ADR-015)."""

from __future__ import annotations

from datetime import date

from app.core.timezone import local_today
from app.models.enums import IssuePriority, IssueStatus
from app.models.issue import Issue
from app.schemas.issue import IssueDetailResponse, IssueListItem


def _days_open(issue: Issue, today: date) -> int:
    return max((today - issue.raised_date).days, 0)


def _days_since_last_update(issue: Issue, today: date) -> int:
    if issue.last_update_at is not None:
        # last_update_at is UTC; its date is close enough for a day-granular metric.
        base = issue.last_update_at.date()
    else:
        base = issue.raised_date
    return max((today - base).days, 0)


def _is_overdue(issue: Issue, today: date) -> bool:
    return (
        issue.status != IssueStatus.CLOSED.value
        and issue.archived_at is None
        and issue.due_date is not None
        and issue.due_date < today
    )


def map_list_item(
    issue: Issue, *, category_name: str | None, responsible_party_name: str | None
) -> IssueListItem:
    today = local_today()
    return IssueListItem(
        id=issue.id,
        issue_code=issue.issue_code,
        title=issue.title,
        category_id=issue.category_id,
        category_name=category_name,
        responsible_party_id=issue.responsible_party_id,
        responsible_party_name=responsible_party_name,
        priority=IssuePriority(issue.priority),
        status=IssueStatus(issue.status),
        raised_date=issue.raised_date,
        pic_name=issue.pic_name,
        pic_user_id=issue.pic_user_id,
        due_date=issue.due_date,
        days_open=_days_open(issue, today),
        last_update_at=issue.last_update_at,
        days_since_last_update=_days_since_last_update(issue, today),
        next_action=issue.next_action,
        is_overdue=_is_overdue(issue, today),
        is_archived=issue.archived_at is not None,
    )


def map_detail(
    issue: Issue, *, category_name: str | None, responsible_party_name: str | None
) -> IssueDetailResponse:
    today = local_today()
    return IssueDetailResponse(
        id=issue.id,
        issue_code=issue.issue_code,
        title=issue.title,
        description=issue.description,
        category_id=issue.category_id,
        category_name=category_name,
        responsible_party_id=issue.responsible_party_id,
        responsible_party_name=responsible_party_name,
        priority=IssuePriority(issue.priority),
        status=IssueStatus(issue.status),
        raised_date=issue.raised_date,
        raised_in_meeting_occurrence_id=issue.raised_in_meeting_occurrence_id,
        pic_name=issue.pic_name,
        pic_user_id=issue.pic_user_id,
        due_date=issue.due_date,
        next_action=issue.next_action,
        last_update_summary=issue.last_update_summary,
        last_update_at=issue.last_update_at,
        closed_date=issue.closed_date,
        closure_note=issue.closure_note,
        reopened_at=issue.reopened_at,
        archived_at=issue.archived_at,
        days_open=_days_open(issue, today),
        days_since_last_update=_days_since_last_update(issue, today),
        is_overdue=_is_overdue(issue, today),
        created_by=issue.created_by,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
    )
