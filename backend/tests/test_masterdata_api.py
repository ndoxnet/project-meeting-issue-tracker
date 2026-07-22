# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import auth_header

pytestmark = pytest.mark.asyncio

CATS = "/api/v1/categories"


async def test_admin_create_category(client, admin_user) -> None:
    resp = await client.post(CATS, json={"name": "Engineering"}, headers=auth_header(admin_user))
    assert resp.status_code == 201
    assert resp.json()["name"] == "Engineering"
    assert resp.json()["is_active"] is True


async def test_duplicate_category_rejected(client, admin_user) -> None:
    await client.post(CATS, json={"name": "Quality"}, headers=auth_header(admin_user))
    resp = await client.post(CATS, json={"name": "quality"}, headers=auth_header(admin_user))
    assert resp.status_code == 409


async def test_update_category(client, admin_user) -> None:
    c = await client.post(CATS, json={"name": "HSE"}, headers=auth_header(admin_user))
    cid = c.json()["id"]
    resp = await client.patch(
        f"{CATS}/{cid}",
        json={"description": "Health, Safety, Environment"},
        headers=auth_header(admin_user),
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Health, Safety, Environment"


async def test_activate_deactivate_category(client, admin_user) -> None:
    c = await client.post(CATS, json={"name": "Schedule"}, headers=auth_header(admin_user))
    cid = c.json()["id"]
    d = await client.post(f"{CATS}/{cid}/deactivate", headers=auth_header(admin_user))
    assert d.json()["is_active"] is False
    a = await client.post(f"{CATS}/{cid}/activate", headers=auth_header(admin_user))
    assert a.json()["is_active"] is True


async def test_viewer_can_read_categories(client, admin_user, viewer_user) -> None:
    await client.post(CATS, json={"name": "Contract"}, headers=auth_header(admin_user))
    resp = await client.get(CATS, headers=auth_header(viewer_user))
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


async def test_viewer_cannot_write_category(client, viewer_user) -> None:
    resp = await client.post(CATS, json={"name": "Nope"}, headers=auth_header(viewer_user))
    assert resp.status_code == 403


async def test_editor_can_create_meeting_occurrence(
    client, admin_user, editor_user, sessionmaker
) -> None:
    # Admin creates the meeting type; editor records an occurrence.
    m = await client.post(
        "/api/v1/meetings",
        json={"name": "Weekly Progress Meeting"},
        headers=auth_header(admin_user),
    )
    meeting_id = m.json()["id"]
    resp = await client.post(
        "/api/v1/meeting-occurrences",
        json={"meeting_id": meeting_id, "meeting_date": "2026-07-20", "meeting_number": "#14"},
        headers=auth_header(editor_user),
    )
    assert resp.status_code == 201
    assert resp.json()["meeting_number"] == "#14"


async def test_editor_cannot_create_meeting_type(client, editor_user) -> None:
    resp = await client.post(
        "/api/v1/meetings", json={"name": "Secret Meeting"}, headers=auth_header(editor_user)
    )
    assert resp.status_code == 403


async def test_category_change_is_audited(client, admin_user, sessionmaker) -> None:
    await client.post(CATS, json={"name": "Procurement"}, headers=auth_header(admin_user))
    async with sessionmaker() as s:
        rows = (
            (await s.execute(select(AuditLog).where(AuditLog.action == "category.create")))
            .scalars()
            .all()
        )
    assert len(rows) == 1
    assert rows[0].actor_user_id == admin_user.id
