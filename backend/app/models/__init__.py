# Concept by MrHan (08974747477)
"""Model registry.

Importing this package imports every model so ``Base.metadata`` is fully
populated (used by Alembic autogenerate and by tests that create all tables).
"""

from __future__ import annotations

from app.db.base import Base
from app.models.app_setting import AppSetting
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.enums import IssuePriority, IssueStatus, UserRole
from app.models.issue import Issue, IssueUpdate
from app.models.issue_counter import IssueCounter
from app.models.meeting import Meeting, MeetingOccurrence
from app.models.responsible_party import ResponsibleParty
from app.models.user import User

__all__ = [
    "Base",
    "AppSetting",
    "Attachment",
    "AuditLog",
    "Category",
    "Issue",
    "IssueUpdate",
    "IssueCounter",
    "Meeting",
    "MeetingOccurrence",
    "ResponsibleParty",
    "User",
    "UserRole",
    "IssuePriority",
    "IssueStatus",
]
