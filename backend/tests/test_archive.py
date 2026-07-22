# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"


async def _new_issue(client, user, category) -> str:
    r = await client.post(ISSUES, json=issue_payload(category.id), headers=auth_header(user))
    return r.json()["issue"]["id"]


async def test_archive_admin_only(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/archive", json={"reason": "duplicate"}, headers=auth_header(editor_user)
    )
    assert r.status_code == 403


async def test_archive_hides_from_default_list(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/archive",
        json={"reason": "entered by mistake"},
        headers=auth_header(admin_user),
    )
    default = await client.get(ISSUES, headers=auth_header(admin_user))
    assert all(i["id"] != iid for i in default.json()["items"])
    incl = await client.get(f"{ISSUES}?include_archived=true", headers=auth_header(admin_user))
    assert any(i["id"] == iid for i in incl.json()["items"])


async def test_no_update_while_archived(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/archive", json={"reason": "mistake"}, headers=auth_header(admin_user)
    )
    r = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "x"},
        headers=auth_header(editor_user),
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ISSUE_ARCHIVED"


async def test_restore_retains_status(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/status",
        json={"new_status": "IN_PROGRESS", "note": "started"},
        headers=auth_header(editor_user),
    )
    await client.post(
        f"{ISSUES}/{iid}/archive", json={"reason": "temp"}, headers=auth_header(admin_user)
    )
    r = await client.post(
        f"{ISSUES}/{iid}/restore", json={"reason": "back"}, headers=auth_header(admin_user)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"
    assert r.json()["archived_at"] is None
