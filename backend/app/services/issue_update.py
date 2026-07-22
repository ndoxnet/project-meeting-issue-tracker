# Concept by MrHan (08974747477)
"""Follow-up updates (append-only) and Admin void (ADR-013).

A follow-up may change status/due/PIC — before/after are captured on the update
row. Void marks an update invalid without rewinding the issue's current state;
if the voided update had changed state, a warning is returned."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.errors import DomainError
from app.core.lifecycle import can_transition
from app.models.enums import IssueStatus
from app.models.issue import IssueUpdate
from app.models.user import User
from app.repositories import issue as issue_repo
from app.services import issue as issue_service
from app.services.audit import record_audit

CURRENT_STATE_NOT_REVERSED = "CURRENT_STATE_NOT_REVERSED"


async def create_follow_up(
    session: AsyncSession, *, issue_id: uuid.UUID, data, actor: User, ctx: RequestContext
) -> IssueUpdate:
    issue = await issue_service.get_issue_or_404(session, issue_id, for_update=True)
    if issue.archived_at is not None:
        raise DomainError(
            "ISSUE_ARCHIVED", "Archived issue cannot receive updates", http_status=409
        )
    if issue.status == IssueStatus.CLOSED.value:
        raise DomainError(
            "ISSUE_ALREADY_CLOSED",
            "Closed issue cannot receive updates; reopen it first",
            http_status=409,
        )
    await issue_service._require_occurrence(session, data.meeting_occurrence_id)

    status_before = status_after = None
    due_before = due_after = None
    pic_before = pic_after = None

    # Status change via follow-up (CLOSED must use the close endpoint).
    if data.new_status is not None and data.new_status.value != issue.status:
        if data.new_status == IssueStatus.CLOSED:
            raise DomainError(
                "INVALID_STATUS_TRANSITION",
                "Use the close endpoint to close an issue",
                http_status=409,
            )
        current = IssueStatus(issue.status)
        if not can_transition(current, data.new_status):
            raise DomainError(
                "INVALID_STATUS_TRANSITION",
                f"Cannot change status from {current.value} to {data.new_status.value}",
                http_status=409,
            )
        status_before = issue.status
        status_after = data.new_status.value
        issue.status = status_after

    if data.new_due_date is not None and data.new_due_date != issue.due_date:
        if data.new_due_date < issue.raised_date:
            raise DomainError(
                "DUE_DATE_BEFORE_RAISED_DATE",
                "Due date cannot be earlier than raised date",
                http_status=422,
            )
        due_before = issue.due_date
        due_after = data.new_due_date
        issue.due_date = due_after

    if data.new_pic_user_id is not None:
        await issue_service._require_active_pic(session, data.new_pic_user_id)
    changing_pic = data.new_pic_name is not None or data.new_pic_user_id is not None
    if changing_pic:
        pic_before = issue.pic_name
        if data.new_pic_name is not None:
            issue.pic_name = data.new_pic_name
        if data.new_pic_user_id is not None:
            issue.pic_user_id = data.new_pic_user_id
        pic_after = issue.pic_name

    if data.next_action is not None:
        issue.next_action = data.next_action

    upd = issue_service._append_update(
        session,
        issue,
        actor=actor,
        update_date=data.update_date,
        meeting_occurrence_id=data.meeting_occurrence_id,
        update_note=data.update_note,
        decision=data.decision,
        next_action=data.next_action,
        action_owner=data.action_owner,
        target_date=data.target_date,
        progress_percentage=data.progress_percentage,
        status_before=status_before,
        status_after=status_after,
        due_date_before=due_before,
        due_date_after=due_after,
        pic_before=pic_before,
        pic_after=pic_after,
    )
    await session.flush()  # assign upd.id before auditing
    record_audit(
        session,
        action="issue_update.create",
        entity_type="issue_update",
        entity_id=upd.id,
        actor_user_id=actor.id,
        after={"issue_id": str(issue.id), "note": data.update_note[:200]},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(upd)
    return upd


async def void_update(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    update_id: uuid.UUID,
    void_reason: str,
    actor: User,
    ctx: RequestContext,
) -> tuple[IssueUpdate, list[str]]:
    upd = await issue_repo.get_update(session, update_id)
    if upd is None or upd.issue_id != issue_id:
        raise DomainError("ISSUE_UPDATE_NOT_FOUND", "Issue update not found", http_status=404)
    if upd.voided_at is not None:
        raise DomainError(
            "ISSUE_UPDATE_ALREADY_VOIDED", "Update is already voided", http_status=409
        )

    upd.voided_at = datetime.now(UTC)
    upd.voided_by = actor.id
    upd.void_reason = void_reason

    warnings: list[str] = []
    # Void does NOT rewind current issue state (ADR-013).
    if upd.status_after is not None or upd.due_date_after is not None or upd.pic_after is not None:
        warnings.append(CURRENT_STATE_NOT_REVERSED)

    record_audit(
        session,
        action="issue_update.void",
        entity_type="issue_update",
        entity_id=upd.id,
        actor_user_id=actor.id,
        after={"update_id": str(upd.id), "reason": void_reason, "warnings": warnings},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(upd)
    return upd, warnings
