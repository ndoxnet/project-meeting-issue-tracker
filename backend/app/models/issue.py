# Concept by MrHan (08974747477)
"""Issue and IssueUpdate models.

Business endpoints for issues arrive in Phase 2B, but the tables are modeled now
so the initial migration is complete. IssueUpdate is append-only (enforced in the
service layer in Phase 2B); no delete-cascade is placed on it that could remove
history.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPKMixin
from app.models.enums import IssuePriority, IssueStatus, values


class Issue(UUIDPKMixin, Base):
    __tablename__ = "issues"
    __table_args__ = (
        CheckConstraint(
            "due_date IS NULL OR due_date >= raised_date",
            name="due_after_raised",
        ),
        CheckConstraint(
            f"priority IN ({', '.join(repr(v) for v in values(IssuePriority))})",
            name="priority_valid",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(v) for v in values(IssueStatus))})",
            name="status_valid",
        ),
        # Composite indexes for the common register/dashboard access patterns
        # (write cost accepted for read speed on filtered lists — see DATABASE.md).
        Index("ix_issues_status_due_date", "status", "due_date"),
        Index("ix_issues_status_last_update_at", "status", "last_update_at"),
        Index("ix_issues_archived_at_status", "archived_at", "status"),
        Index("ix_issues_category_id_status", "category_id", "status"),
        Index("ix_issues_responsible_party_id_status", "responsible_party_id", "status"),
    )

    issue_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    responsible_party_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("responsible_parties.id"), nullable=True, index=True
    )

    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    raised_date: Mapped[date] = mapped_column(Date, nullable=False)
    raised_in_meeting_occurrence_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("meeting_occurrences.id"), nullable=True
    )

    pic_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pic_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Documented denormalization (docs/DATABASE.md): cheap register/dashboard read.
    last_update_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_update_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    closed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closure_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reopened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class IssueUpdate(UUIDPKMixin, Base):
    """Append-only follow-up history for an issue."""

    __tablename__ = "issue_updates"
    __table_args__ = (
        CheckConstraint(
            "progress_percentage IS NULL OR "
            "(progress_percentage >= 0 AND progress_percentage <= 100)",
            name="progress_range",
        ),
    )

    # No ondelete cascade: history must never be removed by deleting an issue.
    issue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("issues.id"), nullable=False, index=True)
    update_date: Mapped[date] = mapped_column(Date, nullable=False)
    meeting_occurrence_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("meeting_occurrences.id"), nullable=True
    )

    update_note: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_owner: Mapped[str | None] = mapped_column(String(150), nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status_before: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status_after: Mapped[str | None] = mapped_column(String(20), nullable=True)
    due_date_before: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date_after: Mapped[date | None] = mapped_column(Date, nullable=True)
    pic_before: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pic_after: Mapped[str | None] = mapped_column(String(150), nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Correction mechanism (Admin-only, Phase 2B): void + replacement update.
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
