# Concept by MrHan (08974747477)
from __future__ import annotations

from app.db.base import Base
from app.schemas.user import UserResponse

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
}


def test_metadata_contains_all_ten_tables() -> None:
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))
    assert len(EXPECTED_TABLES) == 10


def _constraint_names(table_name: str) -> set[str]:
    table = Base.metadata.tables[table_name]
    return {c.name for c in table.constraints if c.name}


def test_issue_updates_progress_constraint_exists() -> None:
    names = _constraint_names("issue_updates")
    assert any("progress_range" in n for n in names)


def test_issues_due_after_raised_constraint_exists() -> None:
    names = _constraint_names("issues")
    assert any("due_after_raised" in n for n in names)


def test_issue_code_unique() -> None:
    col = Base.metadata.tables["issues"].c.issue_code
    assert col.unique is True


def test_users_email_username_unique() -> None:
    users = Base.metadata.tables["users"]
    assert users.c.email.unique is True
    assert users.c.username.unique is True


def test_attachment_stored_filename_unique() -> None:
    assert Base.metadata.tables["attachments"].c.stored_filename.unique is True


def test_issue_indexes_present() -> None:
    issues = Base.metadata.tables["issues"]
    indexed = {c.name for c in issues.columns if c.index}
    # status, due_date, last_update_at, category_id, responsible_party_id, pic_user_id
    for col in ("status", "due_date", "last_update_at", "category_id"):
        assert col in indexed


def test_user_response_has_no_password_field() -> None:
    fields = set(UserResponse.model_fields.keys())
    assert "password" not in fields
    assert "password_hash" not in fields


def test_audit_log_has_no_user_cascade() -> None:
    # actor FK must not cascade-delete audit rows.
    fk = next(
        fk
        for fk in Base.metadata.tables["audit_logs"].foreign_keys
        if fk.column.table.name == "users"
    )
    assert fk.ondelete is None
