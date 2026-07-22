# Concept by MrHan (08974747477)
"""PostgreSQL type + constraint enforcement (proves DB-level rules, not Pydantic)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.core.redaction import REDACTED
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.enums import IssuePriority, IssueStatus, UserRole
from app.models.issue import Issue, IssueUpdate
from app.models.user import User
from app.services.audit import record_audit

pytestmark = [pytest.mark.integration, pytest.mark.postgresql, pytest.mark.asyncio]


def _issue(**over) -> Issue:
    now = datetime.now(UTC)
    base = dict(
        issue_code=f"ISS-2026-{uuid.uuid4().hex[:6]}",
        title="t",
        description="d",
        priority=IssuePriority.HIGH.value,
        status=IssueStatus.OPEN.value,
        raised_date=date(2026, 7, 10),
        created_at=now,
        updated_at=now,
    )
    base.update(over)
    return Issue(**base)


async def _expect_error(pg_sessionmaker, obj, errtypes=(IntegrityError, DBAPIError)):
    with pytest.raises(errtypes):
        async with pg_sessionmaker() as s:
            s.add(obj)
            await s.commit()


# ---- JSONB ----
async def test_jsonb_nested_roundtrip(pg_session, admin_user) -> None:
    payload = {"a": {"b": [1, 2, {"c": "deep"}]}, "flag": True}
    log = AuditLog(
        action="test.jsonb",
        entity_type="issue",
        actor_user_id=admin_user.id,
        before_data=payload,
        after_data={"x": None},
    )
    pg_session.add(log)
    await pg_session.commit()
    fetched = (
        await pg_session.execute(select(AuditLog).where(AuditLog.action == "test.jsonb"))
    ).scalar_one()
    assert fetched.before_data == payload
    assert fetched.after_data == {"x": None}


async def test_jsonb_is_actually_jsonb(pg_session) -> None:
    col_type = (
        await pg_session.execute(
            text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name='audit_logs' AND column_name='before_data'"
            )
        )
    ).scalar_one()
    assert col_type == "jsonb"


async def test_redaction_persists(pg_session, admin_user, category) -> None:
    record_audit(
        pg_session,
        action="test.redact",
        entity_type="user",
        actor_user_id=admin_user.id,
        after={"username": "bob", "password": "supersecret", "token": "abc"},
    )
    await pg_session.commit()
    row = (
        await pg_session.execute(select(AuditLog).where(AuditLog.action == "test.redact"))
    ).scalar_one()
    assert row.after_data["password"] == REDACTED
    assert row.after_data["token"] == REDACTED
    assert row.after_data["username"] == "bob"


# ---- INET ----
async def test_inet_ipv4_ipv6_null(pg_session, admin_user) -> None:
    for ip in ("192.168.1.10", "2001:db8::1", None):
        log = AuditLog(
            action="test.inet", entity_type="user", actor_user_id=admin_user.id, ip_address=ip
        )
        pg_session.add(log)
    await pg_session.commit()
    rows = (
        (await pg_session.execute(select(AuditLog).where(AuditLog.action == "test.inet")))
        .scalars()
        .all()
    )
    assert len(rows) == 3


async def test_inet_type_is_inet(pg_session) -> None:
    col_type = (
        await pg_session.execute(
            text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name='audit_logs' AND column_name='ip_address'"
            )
        )
    ).scalar_one()
    assert col_type == "inet"


async def test_invalid_inet_rejected(pg_sessionmaker, admin_user) -> None:
    bad = AuditLog(
        action="test.badinet",
        entity_type="user",
        actor_user_id=admin_user.id,
        ip_address="not-an-ip",
    )
    await _expect_error(pg_sessionmaker, bad, errtypes=(DBAPIError,))


# ---- CHECK constraints (DB-enforced) ----
async def test_progress_out_of_range_rejected(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(category_id=category.id, created_by=admin_user.id, updated_by=admin_user.id)
    async with pg_sessionmaker() as s:
        s.add(issue)
        await s.commit()
        issue_id = issue.id
    upd = IssueUpdate(
        issue_id=issue_id,
        update_date=date(2026, 7, 11),
        update_note="x",
        progress_percentage=150,
        created_by=admin_user.id,
        created_at=datetime.now(UTC),
    )
    await _expect_error(pg_sessionmaker, upd)


async def test_due_before_raised_rejected_by_db(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(
        category_id=category.id,
        created_by=admin_user.id,
        updated_by=admin_user.id,
        due_date=date(2026, 7, 1),  # before raised 2026-07-10
    )
    await _expect_error(pg_sessionmaker, issue)


async def test_invalid_priority_rejected_by_db(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(
        category_id=category.id,
        created_by=admin_user.id,
        updated_by=admin_user.id,
        priority="URGENT",
    )
    await _expect_error(pg_sessionmaker, issue)


async def test_invalid_status_rejected_by_db(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(
        category_id=category.id,
        created_by=admin_user.id,
        updated_by=admin_user.id,
        status="ARCHIVED",
    )
    await _expect_error(pg_sessionmaker, issue)


async def test_invalid_role_rejected_by_db(pg_sessionmaker) -> None:
    u = User(
        full_name="X",
        email="x@example.com",
        username="xrole",
        password_hash="h",
        role="SUPERUSER",
        is_active=True,
    )
    await _expect_error(pg_sessionmaker, u)


async def test_attachment_negative_size_rejected(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(category_id=category.id, created_by=admin_user.id, updated_by=admin_user.id)
    async with pg_sessionmaker() as s:
        s.add(issue)
        await s.commit()
        issue_id = issue.id
    att = Attachment(
        issue_id=issue_id,
        original_filename="a.pdf",
        stored_filename=uuid.uuid4().hex,
        storage_path="/tmp/x",
        mime_type="application/pdf",
        size_bytes=-1,
        uploaded_by=admin_user.id,
    )
    await _expect_error(pg_sessionmaker, att)


# ---- UNIQUE ----
async def test_duplicate_issue_code_rejected(pg_sessionmaker, admin_user, category) -> None:
    code = "ISS-2026-9999"
    async with pg_sessionmaker() as s:
        s.add(
            _issue(
                issue_code=code,
                category_id=category.id,
                created_by=admin_user.id,
                updated_by=admin_user.id,
            )
        )
        await s.commit()
    await _expect_error(
        pg_sessionmaker,
        _issue(
            issue_code=code,
            category_id=category.id,
            created_by=admin_user.id,
            updated_by=admin_user.id,
        ),
    )


async def test_duplicate_email_rejected(pg_sessionmaker) -> None:
    async with pg_sessionmaker() as s:
        s.add(
            User(
                full_name="A",
                email="dup@example.com",
                username="a1",
                password_hash="h",
                role=UserRole.EDITOR.value,
                is_active=True,
            )
        )
        await s.commit()
    await _expect_error(
        pg_sessionmaker,
        User(
            full_name="B",
            email="dup@example.com",
            username="a2",
            password_hash="h",
            role=UserRole.EDITOR.value,
            is_active=True,
        ),
    )


async def test_duplicate_username_rejected(pg_sessionmaker) -> None:
    async with pg_sessionmaker() as s:
        s.add(
            User(
                full_name="A",
                email="u1@example.com",
                username="dupuser",
                password_hash="h",
                role=UserRole.EDITOR.value,
                is_active=True,
            )
        )
        await s.commit()
    await _expect_error(
        pg_sessionmaker,
        User(
            full_name="B",
            email="u2@example.com",
            username="dupuser",
            password_hash="h",
            role=UserRole.EDITOR.value,
            is_active=True,
        ),
    )


# ---- FOREIGN KEYS ----
async def test_invalid_category_fk_rejected(pg_sessionmaker, admin_user) -> None:
    issue = _issue(category_id=uuid.uuid4(), created_by=admin_user.id, updated_by=admin_user.id)
    await _expect_error(pg_sessionmaker, issue)


async def test_invalid_creator_fk_rejected(pg_sessionmaker, category) -> None:
    issue = _issue(category_id=category.id, created_by=uuid.uuid4(), updated_by=None)
    await _expect_error(pg_sessionmaker, issue)


async def test_invalid_occurrence_fk_rejected(pg_sessionmaker, admin_user, category) -> None:
    issue = _issue(
        category_id=category.id,
        created_by=admin_user.id,
        updated_by=admin_user.id,
        raised_in_meeting_occurrence_id=uuid.uuid4(),
    )
    await _expect_error(pg_sessionmaker, issue)
