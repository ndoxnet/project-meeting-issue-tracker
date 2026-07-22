# Concept by MrHan (08974747477)
"""Transaction atomicity via fault injection: if audit creation fails, the whole
operation rolls back (no partial state, no orphan history) on PostgreSQL."""

from __future__ import annotations

import pytest

from tests.conftest import auth_header
from tests.integration.conftest import issue_payload

pytestmark = [pytest.mark.integration, pytest.mark.postgresql, pytest.mark.asyncio]
ISSUES = "/api/v1/issues"


def _boom(*args, **kwargs):
    raise RuntimeError("injected audit failure")


async def _new_issue(client, hdr, category) -> str:
    r = await client.post(ISSUES, json=issue_payload(category.id), headers=hdr)
    return r.json()["issue"]["id"]


async def test_followup_rolls_back_on_audit_failure(
    pg_client, editor_user, category, monkeypatch
) -> None:
    hdr = auth_header(editor_user)
    iid = await _new_issue(pg_client, hdr, category)
    monkeypatch.setattr("app.services.issue_update.record_audit", _boom)
    r = await pg_client.post(
        f"{ISSUES}/{iid}/updates",
        json={
            "update_date": "2026-07-17",
            "update_note": "should not persist",
            "new_status": "IN_PROGRESS",
        },
        headers=hdr,
    )
    assert r.status_code == 500
    monkeypatch.undo()
    # State unchanged: still OPEN, only the initial "Issue raised" update exists.
    detail = await pg_client.get(f"{ISSUES}/{iid}", headers=hdr)
    assert detail.json()["status"] == "OPEN"
    updates = await pg_client.get(f"{ISSUES}/{iid}/updates", headers=hdr)
    assert len(updates.json()) == 1


async def test_close_rolls_back_on_audit_failure(
    pg_client, editor_user, category, monkeypatch
) -> None:
    hdr = auth_header(editor_user)
    iid = await _new_issue(pg_client, hdr, category)
    monkeypatch.setattr("app.services.issue.record_audit", _boom)
    r = await pg_client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-08-05"},
        headers=hdr,
    )
    assert r.status_code == 500
    monkeypatch.undo()
    detail = await pg_client.get(f"{ISSUES}/{iid}", headers=hdr)
    body = detail.json()
    assert body["status"] == "OPEN"
    assert body["closed_date"] is None
    assert body["closure_note"] is None


async def test_reopen_rolls_back_on_audit_failure(
    pg_client, editor_user, category, monkeypatch
) -> None:
    hdr = auth_header(editor_user)
    iid = await _new_issue(pg_client, hdr, category)
    await pg_client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-08-05"},
        headers=hdr,
    )
    monkeypatch.setattr("app.services.issue.record_audit", _boom)
    r = await pg_client.post(
        f"{ISSUES}/{iid}/reopen",
        json={"reason": "recheck", "reopen_date": "2026-08-10"},
        headers=hdr,
    )
    assert r.status_code == 500
    monkeypatch.undo()
    detail = await pg_client.get(f"{ISSUES}/{iid}", headers=hdr)
    assert detail.json()["status"] == "CLOSED"
    assert detail.json()["reopened_at"] is None


async def test_archive_rolls_back_on_audit_failure(
    pg_client, admin_user, category, monkeypatch
) -> None:
    hdr = auth_header(admin_user)
    iid = await _new_issue(pg_client, hdr, category)
    monkeypatch.setattr("app.services.issue.record_audit", _boom)
    r = await pg_client.post(f"{ISSUES}/{iid}/archive", json={"reason": "x"}, headers=hdr)
    assert r.status_code == 500
    monkeypatch.undo()
    detail = await pg_client.get(f"{ISSUES}/{iid}", headers=hdr)
    assert detail.json()["archived_at"] is None


async def test_create_rolls_back_on_audit_failure(
    pg_client, pg_sessionmaker, editor_user, category, monkeypatch
) -> None:
    from sqlalchemy import func, select

    from app.models.issue import Issue

    hdr = auth_header(editor_user)
    monkeypatch.setattr("app.services.issue.record_audit", _boom)
    r = await pg_client.post(ISSUES, json=issue_payload(category.id), headers=hdr)
    assert r.status_code == 500
    monkeypatch.undo()
    # No issue row persisted despite the counter having been touched in the
    # rolled-back transaction.
    async with pg_sessionmaker() as s:
        count = (await s.execute(select(func.count()).select_from(Issue))).scalar_one()
    assert count == 0
