# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from app.db.base import Base
from app.repositories import issue as issue_repo

EXPECTED_TABLES = {
    "users",
    "categories",
    "responsible_parties",
    "meetings",
    "meeting_occurrences",
    "issues",
    "issue_updates",
    "attachments",
    "audit_logs",
    "app_settings",
    "issue_counters",
}


def test_metadata_contains_eleven_tables() -> None:
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))
    assert len(EXPECTED_TABLES) == 11


def test_issue_composite_indexes_present() -> None:
    idx_names = {ix.name for ix in Base.metadata.tables["issues"].indexes}
    for name in (
        "ix_issues_status_due_date",
        "ix_issues_status_last_update_at",
        "ix_issues_archived_at_status",
        "ix_issues_category_id_status",
        "ix_issues_responsible_party_id_status",
    ):
        assert name in idx_names


@pytest.mark.asyncio
async def test_counter_increments(db_session) -> None:
    n1 = await issue_repo.next_issue_number(db_session, 2026)
    n2 = await issue_repo.next_issue_number(db_session, 2026)
    n3 = await issue_repo.next_issue_number(db_session, 2027)
    assert (n1, n2, n3) == (1, 2, 1)


def test_sortable_allowlist_excludes_sensitive() -> None:
    # The sort allow-list must not expose arbitrary columns.
    assert "password_hash" not in issue_repo.SORTABLE
    assert set(issue_repo.SORTABLE) == {
        "issue_code",
        "raised_date",
        "due_date",
        "last_update_at",
        "updated_at",
        "priority",
        "status",
    }
