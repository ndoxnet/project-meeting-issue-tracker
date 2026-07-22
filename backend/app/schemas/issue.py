# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import IssuePriority, IssueStatus


# ---------- create / update ----------
class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1)
    category_id: uuid.UUID
    responsible_party_id: uuid.UUID | None = None
    priority: IssuePriority = IssuePriority.MEDIUM
    raised_date: date
    raised_in_meeting_occurrence_id: uuid.UUID | None = None
    pic_name: str | None = Field(default=None, max_length=150)
    pic_user_id: uuid.UUID | None = None
    due_date: date | None = None
    next_action: str | None = None
    # Optional acknowledgement to proceed despite a possible-duplicate warning.
    confirm_possible_duplicate: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Vendor commissioning attendance is pending",
                    "description": "Vendor engineer not yet mobilized for Area 5 commissioning.",
                    "category_id": "3f1c9d2e-0000-4000-8000-000000000001",
                    "priority": "HIGH",
                    "raised_date": "2026-07-10",
                    "due_date": "2026-08-01",
                    "pic_name": "Budi Santoso",
                    "next_action": "Vendor to confirm mobilization date",
                }
            ]
        }
    }


class IssueMetadataUpdate(BaseModel):
    """Generic metadata edit. Status/close/reopen/archive use dedicated endpoints."""

    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, min_length=1)
    category_id: uuid.UUID | None = None
    responsible_party_id: uuid.UUID | None = None
    priority: IssuePriority | None = None
    pic_name: str | None = Field(default=None, max_length=150)
    pic_user_id: uuid.UUID | None = None
    due_date: date | None = None
    next_action: str | None = None
    # Required when changing PIC or due date (avoids ambiguous history).
    change_reason: str | None = Field(default=None, max_length=500)


# ---------- lifecycle actions ----------
class IssueStatusChangeRequest(BaseModel):
    new_status: IssueStatus
    note: str = Field(min_length=1, max_length=1000)
    meeting_occurrence_id: uuid.UUID | None = None


class IssueCloseRequest(BaseModel):
    closure_note: str = Field(min_length=1)
    closed_date: date
    meeting_occurrence_id: uuid.UUID | None = None
    final_update_note: str | None = None


class IssueReopenRequest(BaseModel):
    reason: str = Field(min_length=1)
    reopen_date: date
    meeting_occurrence_id: uuid.UUID | None = None
    new_due_date: date | None = None
    next_action: str | None = None
    new_pic_name: str | None = Field(default=None, max_length=150)
    new_pic_user_id: uuid.UUID | None = None


class IssueArchiveRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class IssueRestoreRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


# ---------- follow-up updates ----------
class IssueUpdateCreate(BaseModel):
    update_date: date
    meeting_occurrence_id: uuid.UUID | None = None
    update_note: str = Field(min_length=1)
    decision: str | None = None
    next_action: str | None = None
    action_owner: str | None = Field(default=None, max_length=150)
    target_date: date | None = None
    progress_percentage: int | None = Field(default=None, ge=0, le=100)
    new_status: IssueStatus | None = None
    new_due_date: date | None = None
    new_pic_name: str | None = Field(default=None, max_length=150)
    new_pic_user_id: uuid.UUID | None = None


class IssueUpdateVoidRequest(BaseModel):
    void_reason: str = Field(min_length=3, max_length=500)


class IssueUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    issue_id: uuid.UUID
    update_date: date
    meeting_occurrence_id: uuid.UUID | None
    update_note: str
    decision: str | None
    next_action: str | None
    action_owner: str | None
    target_date: date | None
    progress_percentage: int | None
    status_before: str | None
    status_after: str | None
    due_date_before: date | None
    due_date_after: date | None
    pic_before: str | None
    pic_after: str | None
    created_by: uuid.UUID
    created_at: datetime
    voided_at: datetime | None
    voided_by: uuid.UUID | None
    void_reason: str | None


# ---------- responses ----------
class IssueListItem(BaseModel):
    id: uuid.UUID
    issue_code: str
    title: str
    category_id: uuid.UUID
    category_name: str | None
    responsible_party_id: uuid.UUID | None
    responsible_party_name: str | None
    priority: IssuePriority
    status: IssueStatus
    raised_date: date
    pic_name: str | None
    pic_user_id: uuid.UUID | None
    due_date: date | None
    days_open: int
    last_update_at: datetime | None
    days_since_last_update: int
    next_action: str | None
    is_overdue: bool
    is_archived: bool


class IssueDetailResponse(BaseModel):
    id: uuid.UUID
    issue_code: str
    title: str
    description: str
    category_id: uuid.UUID
    category_name: str | None
    responsible_party_id: uuid.UUID | None
    responsible_party_name: str | None
    priority: IssuePriority
    status: IssueStatus
    raised_date: date
    raised_in_meeting_occurrence_id: uuid.UUID | None
    pic_name: str | None
    pic_user_id: uuid.UUID | None
    due_date: date | None
    next_action: str | None
    last_update_summary: str | None
    last_update_at: datetime | None
    closed_date: date | None
    closure_note: str | None
    reopened_at: datetime | None
    archived_at: datetime | None
    days_open: int
    days_since_last_update: int
    is_overdue: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DuplicateWarning(BaseModel):
    code: str = "POSSIBLE_DUPLICATE"
    issue_id: uuid.UUID
    issue_code: str
    title: str


class IssueCreateResponse(BaseModel):
    issue: IssueDetailResponse
    warnings: list[DuplicateWarning] = []


class VoidResponse(BaseModel):
    update: IssueUpdateResponse
    warnings: list[str] = []
