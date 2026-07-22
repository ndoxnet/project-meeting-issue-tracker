# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"


async def _new_issue(client, user, category, **over) -> str:
    r = await client.post(
        ISSUES, json=issue_payload(category.id, **over), headers=auth_header(user)
    )
    assert r.status_code == 201
    return r.json()["issue"]["id"]


async def _status(client, user, iid, new_status, note="progress"):
    return await client.post(
        f"{ISSUES}/{iid}/status",
        json={"new_status": new_status, "note": note},
        headers=auth_header(user),
    )


async def test_open_to_in_progress(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _status(client, editor_user, iid, "IN_PROGRESS")
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"


async def test_status_change_records_history(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await _status(client, editor_user, iid, "IN_PROGRESS")
    updates = await client.get(f"{ISSUES}/{iid}/updates", headers=auth_header(editor_user))
    changes = [u for u in updates.json() if u["status_after"] == "IN_PROGRESS"]
    assert len(changes) == 1
    assert changes[0]["status_before"] == "OPEN"


async def test_close_via_status_endpoint_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _status(client, editor_user, iid, "CLOSED")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


async def test_invalid_transition_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    # OPEN -> REOPENED is not a valid generic transition.
    r = await _status(client, editor_user, iid, "REOPENED")
    assert r.status_code == 409


async def test_close_requires_note(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closed_date": "2026-08-05"},  # missing closure_note
        headers=auth_header(editor_user),
    )
    assert r.status_code == 422


async def test_close_date_before_raised_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-07-01"},
        headers=auth_header(editor_user),
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "DUE_DATE_BEFORE_RAISED_DATE"


async def test_close_then_double_close_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r1 = await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "verified", "closed_date": "2026-08-05"},
        headers=auth_header(editor_user),
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "CLOSED"
    assert r1.json()["next_action"] is None  # cleared on close
    r2 = await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "again", "closed_date": "2026-08-06"},
        headers=auth_header(editor_user),
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ISSUE_ALREADY_CLOSED"


async def test_closed_issue_rejects_metadata_update(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-08-05"},
        headers=auth_header(editor_user),
    )
    r = await client.patch(
        f"{ISSUES}/{iid}", json={"title": "new title"}, headers=auth_header(editor_user)
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ISSUE_ALREADY_CLOSED"


async def test_reopen_flow(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-08-05"},
        headers=auth_header(editor_user),
    )
    r = await client.post(
        f"{ISSUES}/{iid}/reopen",
        json={"reason": "Defect recurred", "reopen_date": "2026-08-10"},
        headers=auth_header(editor_user),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "REOPENED"
    assert body["reopened_at"] is not None
    # Previous closure retained.
    assert body["closed_date"] == "2026-08-05"
    assert body["closure_note"] == "done"


async def test_reopen_non_closed_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/reopen",
        json={"reason": "x", "reopen_date": "2026-08-10"},
        headers=auth_header(editor_user),
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ISSUE_NOT_CLOSED"


async def test_reopened_can_transition(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": "2026-08-05"},
        headers=auth_header(editor_user),
    )
    await client.post(
        f"{ISSUES}/{iid}/reopen",
        json={"reason": "recheck", "reopen_date": "2026-08-10"},
        headers=auth_header(editor_user),
    )
    r = await _status(client, editor_user, iid, "IN_PROGRESS")
    assert r.status_code == 200
