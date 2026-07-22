# Concept by MrHan (08974747477)
"""Issue lifecycle service.

All operations are atomic (the service owns the transaction boundary): each
change writes an append-only issue_update (where applicable) plus an audit row and
commits once. See ADR-011 (issue code), ADR-012 (lifecycle), ADR-013 (void).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.lifecycle import can_transition
from app.core.timezone import local_today
from app.models.category import Category
from app.models.enums import IssueStatus
from app.models.issue import Issue, IssueUpdate
from app.models.responsible_party import ResponsibleParty
from app.models.user import User
from app.repositories import issue as issue_repo
from app.repositories import masterdata as md_repo
from app.repositories import user as user_repo
from app.services.audit import record_audit

_SUMMARY_MAX = 500


def _issue_public(issue: Issue) -> dict:
    return {
        "id": str(issue.id),
        "issue_code": issue.issue_code,
        "title": issue.title,
        "status": issue.status,
        "priority": issue.priority,
        "pic_name": issue.pic_name,
        "due_date": issue.due_date.isoformat() if issue.due_date else None,
        "archived": issue.archived_at is not None,
    }


def _append_update(
    session: AsyncSession,
    issue: Issue,
    *,
    actor: User,
    update_date: date,
    update_note: str,
    meeting_occurrence_id: uuid.UUID | None = None,
    decision: str | None = None,
    next_action: str | None = None,
    action_owner: str | None = None,
    target_date: date | None = None,
    progress_percentage: int | None = None,
    status_before: str | None = None,
    status_after: str | None = None,
    due_date_before: date | None = None,
    due_date_after: date | None = None,
    pic_before: str | None = None,
    pic_after: str | None = None,
    touch_last_update: bool = True,
) -> IssueUpdate:
    now = datetime.now(UTC)
    upd = IssueUpdate(
        issue_id=issue.id,
        update_date=update_date,
        meeting_occurrence_id=meeting_occurrence_id,
        update_note=update_note,
        decision=decision,
        next_action=next_action,
        action_owner=action_owner,
        target_date=target_date,
        progress_percentage=progress_percentage,
        status_before=status_before,
        status_after=status_after,
        due_date_before=due_date_before,
        due_date_after=due_date_after,
        pic_before=pic_before,
        pic_after=pic_after,
        created_by=actor.id,
        created_at=now,
    )
    session.add(upd)
    # The initial "Issue raised" event does not count as a follow-up: leaving
    # last_update_at null lets stagnant/last-update fall back to raised_date.
    if touch_last_update:
        issue.last_update_summary = update_note[:_SUMMARY_MAX]
        issue.last_update_at = now
    issue.updated_at = now
    issue.updated_by = actor.id
    return upd


# ---------- validation helpers ----------
async def _require_active_category(session: AsyncSession, category_id: uuid.UUID) -> Category:
    cat = await md_repo.get_named(session, Category, category_id)
    if cat is None:
        raise DomainError("CATEGORY_INACTIVE", "Category not found", http_status=422)
    if not cat.is_active:
        raise DomainError("CATEGORY_INACTIVE", "Category is inactive", http_status=422)
    return cat


async def _require_active_rp(
    session: AsyncSession, rp_id: uuid.UUID | None
) -> ResponsibleParty | None:
    if rp_id is None:
        return None
    rp = await md_repo.get_named(session, ResponsibleParty, rp_id)
    if rp is None or not rp.is_active:
        raise DomainError(
            "RESPONSIBLE_PARTY_INACTIVE", "Responsible party is inactive", http_status=422
        )
    return rp


async def _require_active_pic(session: AsyncSession, pic_user_id: uuid.UUID | None) -> None:
    if pic_user_id is None:
        return
    u = await user_repo.get_by_id(session, pic_user_id)
    if u is None or not u.is_active:
        raise DomainError("PIC_USER_INACTIVE", "PIC user is inactive", http_status=422)


async def _require_occurrence(session: AsyncSession, occ_id: uuid.UUID | None) -> None:
    if occ_id is None:
        return
    occ = await md_repo.get_occurrence(session, occ_id)
    if occ is None:
        raise DomainError(
            "MEETING_OCCURRENCE_NOT_FOUND", "Meeting occurrence not found", http_status=404
        )


async def get_issue_or_404(
    session: AsyncSession, issue_id: uuid.UUID, *, for_update: bool = False
) -> Issue:
    issue = await issue_repo.get_issue(session, issue_id, for_update=for_update)
    if issue is None:
        raise DomainError("ISSUE_NOT_FOUND", "Issue not found", http_status=404)
    return issue


# ---------- create ----------
async def create_issue(
    session: AsyncSession, *, data, actor: User, ctx: RequestContext
) -> tuple[Issue, list[Issue]]:
    """Create an issue. Returns (issue, possible_duplicates). Atomic."""
    if data.due_date is not None and data.due_date < data.raised_date:
        raise DomainError(
            "DUE_DATE_BEFORE_RAISED_DATE",
            "Due date cannot be earlier than raised date",
            http_status=422,
        )
    await _require_active_category(session, data.category_id)
    await _require_active_rp(session, data.responsible_party_id)
    await _require_active_pic(session, data.pic_user_id)
    await _require_occurrence(session, data.raised_in_meeting_occurrence_id)

    duplicates = await issue_repo.find_possible_duplicates(
        session, title=data.title, category_id=data.category_id
    )

    settings = get_settings()
    prefix = settings.ISSUE_CODE_PREFIX
    year = data.raised_date.year

    last_error: Exception | None = None
    for _attempt in range(3):
        try:
            number = await issue_repo.next_issue_number(session, year)
            code = f"{prefix}-{year}-{number:04d}"
            now = datetime.now(UTC)
            issue = Issue(
                issue_code=code,
                title=data.title.strip(),
                description=data.description,
                category_id=data.category_id,
                responsible_party_id=data.responsible_party_id,
                priority=data.priority.value,
                status=IssueStatus.OPEN.value,
                raised_date=data.raised_date,
                raised_in_meeting_occurrence_id=data.raised_in_meeting_occurrence_id,
                pic_name=data.pic_name,
                pic_user_id=data.pic_user_id,
                due_date=data.due_date,
                next_action=data.next_action,
                created_by=actor.id,
                created_at=now,
                updated_by=actor.id,
                updated_at=now,
            )
            session.add(issue)
            await session.flush()
            _append_update(
                session,
                issue,
                actor=actor,
                update_date=data.raised_date,
                meeting_occurrence_id=data.raised_in_meeting_occurrence_id,
                update_note="Issue raised.",
                status_after=IssueStatus.OPEN.value,
                touch_last_update=False,
            )
            record_audit(
                session,
                action="issue.create",
                entity_type="issue",
                entity_id=issue.id,
                actor_user_id=actor.id,
                after=_issue_public(issue),
                ctx=ctx,
            )
            await session.commit()
            await session.refresh(issue)
            return issue, duplicates
        except IntegrityError as exc:  # issue_code unique guard raced
            last_error = exc
            await session.rollback()
    raise DomainError(
        "CONFLICT", "Could not allocate a unique issue code", http_status=409
    ) from last_error


# ---------- metadata update ----------
async def update_metadata(
    session: AsyncSession, *, issue_id: uuid.UUID, data, actor: User, ctx: RequestContext
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError("ISSUE_ARCHIVED", "Issue is archived", http_status=409)
    if issue.status == IssueStatus.CLOSED.value:
        raise DomainError(
            "ISSUE_ALREADY_CLOSED",
            "Closed issue cannot be edited; reopen it first",
            http_status=409,
        )

    changing_pic = data.pic_name is not None or data.pic_user_id is not None
    changing_due = data.due_date is not None
    if (changing_pic or changing_due) and not (data.change_reason and data.change_reason.strip()):
        raise DomainError(
            "VALIDATION_ERROR",
            "change_reason is required when changing PIC or due date",
            http_status=422,
        )

    before = _issue_public(issue)
    pic_before = issue.pic_name
    due_before = issue.due_date

    if data.category_id is not None:
        await _require_active_category(session, data.category_id)
        issue.category_id = data.category_id
    if data.responsible_party_id is not None:
        await _require_active_rp(session, data.responsible_party_id)
        issue.responsible_party_id = data.responsible_party_id
    if data.pic_user_id is not None:
        await _require_active_pic(session, data.pic_user_id)
        issue.pic_user_id = data.pic_user_id
    if data.title is not None:
        issue.title = data.title.strip()
    if data.description is not None:
        issue.description = data.description
    if data.priority is not None:
        issue.priority = data.priority.value
    if data.pic_name is not None:
        issue.pic_name = data.pic_name
    if data.next_action is not None:
        issue.next_action = data.next_action
    if data.due_date is not None:
        if data.due_date < issue.raised_date:
            raise DomainError(
                "DUE_DATE_BEFORE_RAISED_DATE",
                "Due date cannot be earlier than raised date",
                http_status=422,
            )
        issue.due_date = data.due_date

    # Record an issue_update for material changes (PIC / due / next action).
    if changing_pic or changing_due or data.next_action is not None:
        _append_update(
            session,
            issue,
            actor=actor,
            update_date=local_today(),
            update_note=(data.change_reason or "Issue metadata updated"),
            next_action=data.next_action,
            due_date_before=due_before if changing_due else None,
            due_date_after=issue.due_date if changing_due else None,
            pic_before=pic_before if changing_pic else None,
            pic_after=issue.pic_name if changing_pic else None,
        )
    else:
        issue.updated_at = datetime.now(UTC)
        issue.updated_by = actor.id

    record_audit(
        session,
        action="issue.update",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after=_issue_public(issue),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue


# ---------- status change ----------
async def change_status(
    session: AsyncSession, *, issue_id: uuid.UUID, data, actor: User, ctx: RequestContext
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError("ISSUE_ARCHIVED", "Issue is archived", http_status=409)

    current = IssueStatus(issue.status)
    target = data.new_status
    if target == IssueStatus.CLOSED:
        raise DomainError(
            "INVALID_STATUS_TRANSITION",
            "Use the close endpoint to close an issue",
            http_status=409,
        )
    if not can_transition(current, target):
        raise DomainError(
            "INVALID_STATUS_TRANSITION",
            f"Cannot change status from {current.value} to {target.value}",
            http_status=409,
        )
    await _require_occurrence(session, data.meeting_occurrence_id)

    before = _issue_public(issue)
    issue.status = target.value
    _append_update(
        session,
        issue,
        actor=actor,
        update_date=local_today(),
        meeting_occurrence_id=data.meeting_occurrence_id,
        update_note=data.note,
        status_before=current.value,
        status_after=target.value,
    )
    record_audit(
        session,
        action="issue.status_change",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after=_issue_public(issue),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue


# ---------- close ----------
async def close_issue(
    session: AsyncSession, *, issue_id: uuid.UUID, data, actor: User, ctx: RequestContext
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError("ISSUE_ARCHIVED", "Issue is archived", http_status=409)
    if issue.status == IssueStatus.CLOSED.value:
        raise DomainError("ISSUE_ALREADY_CLOSED", "Issue is already closed", http_status=409)
    if data.closed_date < issue.raised_date:
        raise DomainError(
            "DUE_DATE_BEFORE_RAISED_DATE",
            "Closed date cannot be earlier than raised date",
            http_status=422,
        )
    await _require_occurrence(session, data.meeting_occurrence_id)

    before = _issue_public(issue)
    status_before = issue.status
    issue.status = IssueStatus.CLOSED.value
    issue.closed_date = data.closed_date
    issue.closure_note = data.closure_note
    # Decision (documented): keep the last next_action in history but clear the
    # current one on close.
    issue.next_action = None
    _append_update(
        session,
        issue,
        actor=actor,
        update_date=data.closed_date,
        meeting_occurrence_id=data.meeting_occurrence_id,
        update_note=data.final_update_note or f"Issue closed. {data.closure_note}",
        status_before=status_before,
        status_after=IssueStatus.CLOSED.value,
    )
    record_audit(
        session,
        action="issue.close",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after=_issue_public(issue),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue


# ---------- reopen ----------
async def reopen_issue(
    session: AsyncSession, *, issue_id: uuid.UUID, data, actor: User, ctx: RequestContext
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError("ISSUE_ARCHIVED", "Restore the issue before reopening", http_status=409)
    if issue.status != IssueStatus.CLOSED.value:
        raise DomainError(
            "ISSUE_NOT_CLOSED", "Only a closed issue can be reopened", http_status=409
        )
    await _require_occurrence(session, data.meeting_occurrence_id)
    await _require_active_pic(session, data.new_pic_user_id)

    before = _issue_public(issue)
    due_before = issue.due_date
    pic_before = issue.pic_name
    issue.status = IssueStatus.REOPENED.value
    issue.reopened_at = datetime.now(UTC)
    # closed_date / closure_note are retained as the last closure (ADR-012).
    changed_due = data.new_due_date is not None
    if changed_due:
        if data.new_due_date < issue.raised_date:
            raise DomainError(
                "DUE_DATE_BEFORE_RAISED_DATE",
                "Due date cannot be earlier than raised date",
                http_status=422,
            )
        issue.due_date = data.new_due_date
    if data.next_action is not None:
        issue.next_action = data.next_action
    changed_pic = data.new_pic_name is not None or data.new_pic_user_id is not None
    if data.new_pic_name is not None:
        issue.pic_name = data.new_pic_name
    if data.new_pic_user_id is not None:
        issue.pic_user_id = data.new_pic_user_id

    _append_update(
        session,
        issue,
        actor=actor,
        update_date=data.reopen_date,
        meeting_occurrence_id=data.meeting_occurrence_id,
        update_note=f"Issue reopened. {data.reason}",
        next_action=data.next_action,
        status_before=IssueStatus.CLOSED.value,
        status_after=IssueStatus.REOPENED.value,
        due_date_before=due_before if changed_due else None,
        due_date_after=issue.due_date if changed_due else None,
        pic_before=pic_before if changed_pic else None,
        pic_after=issue.pic_name if changed_pic else None,
    )
    record_audit(
        session,
        action="issue.reopen",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after=_issue_public(issue),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue


# ---------- archive / restore ----------
async def archive_issue(
    session: AsyncSession, *, issue_id: uuid.UUID, reason: str, actor: User, ctx: RequestContext
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError("ISSUE_ARCHIVED", "Issue is already archived", http_status=409)
    before = _issue_public(issue)
    issue.archived_at = datetime.now(UTC)
    issue.archived_by = actor.id
    record_audit(
        session,
        action="issue.archive",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after={**_issue_public(issue), "reason": reason},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue


async def restore_issue(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    reason: str | None,
    actor: User,
    ctx: RequestContext,
) -> Issue:
    issue = await get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is None:
        raise DomainError("VALIDATION_ERROR", "Issue is not archived", http_status=409)
    before = _issue_public(issue)
    issue.archived_at = None
    issue.archived_by = None
    record_audit(
        session,
        action="issue.restore",
        entity_type="issue",
        entity_id=issue.id,
        actor_user_id=actor.id,
        before=before,
        after={**_issue_public(issue), "reason": reason},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(issue)
    return issue
