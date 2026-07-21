# Concept by MrHan (08974747477)
"""Application enums.

Decision (documented in docs/DATABASE.md): use string-backed enums stored as
VARCHAR with CHECK constraints, rather than native PostgreSQL ENUM types. This is
portable (works on SQLite for tests), easy to evolve (no ALTER TYPE dance), and
simple to validate. String length is bounded and a CHECK constraint enforces the
allowed set at the database level.
"""
from __future__ import annotations

import enum


class UserRole(enum.StrEnum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class IssuePriority(enum.StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueStatus(enum.StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


def values(e: type[enum.Enum]) -> list[str]:
    """Return the string values of an enum (used to build CHECK constraints)."""
    return [member.value for member in e]
