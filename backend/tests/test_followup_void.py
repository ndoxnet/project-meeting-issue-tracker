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
    return r.json()["issue"]["id"]


async def test_followup_outside_meeting(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "Contractor mobilizing manpower"},
        headers=auth_header(editor_user),
    )
    assert r.status_code == 201
    assert r.json()["meeting_occurrence_id"] is None


async def test_followup_meeting_linked(client, editor_user, category, occurrence) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={
            "update_date": "2026-07-17",
            "meeting_occurrence_id": str(occurrence.id),
            "update_note": "Discussed in construction meeting",
        },
        headers=auth_header(editor_user),
    )
    assert r.status_code == 201
    assert r.json()["meeting_occurrence_id"] == str(occurrence.id)


async def test_followup_status_due_pic_captured(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={
            "update_date": "2026-07-17",
            "update_note": "Progress and reassignment",
            "new_status": "IN_PROGRESS",
            "new_due_date": "2026-09-01",
            "new_pic_name": "Budi",
            "progress_percentage": 65,
        },
        headers=auth_header(editor_user),
    )
    assert r.status_code == 201
    u = r.json()
    assert u["status_before"] == "OPEN" and u["status_after"] == "IN_PROGRESS"
    assert u["due_date_after"] == "2026-09-01"
    assert u["pic_after"] == "Budi"
    assert u["progress_percentage"] == 65
    # Issue current state reflects the change.
    detail = await client.get(f"{ISSUES}/{iid}", headers=auth_header(editor_user))
    assert detail.json()["status"] == "IN_PROGRESS"
    assert detail.json()["last_update_at"] is not None


async def test_viewer_cannot_create_update(client, viewer_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "x"},
        headers=auth_header(viewer_user),
    )
    assert r.status_code == 403


async def test_viewer_can_read_updates(client, viewer_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await client.get(f"{ISSUES}/{iid}/updates", headers=auth_header(viewer_user))
    assert r.status_code == 200
    # The creation "Issue raised." update exists.
    assert any(u["update_note"] == "Issue raised." for u in r.json())


async def test_void_admin_only(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    upd = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "note"},
        headers=auth_header(editor_user),
    )
    update_id = upd.json()["id"]
    r = await client.post(
        f"{ISSUES}/{iid}/updates/{update_id}/void",
        json={"void_reason": "entered on wrong issue"},
        headers=auth_header(editor_user),  # editor forbidden
    )
    assert r.status_code == 403


async def test_void_state_not_reversed_warning(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    upd = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "status bump", "new_status": "PENDING"},
        headers=auth_header(editor_user),
    )
    update_id = upd.json()["id"]
    r = await client.post(
        f"{ISSUES}/{iid}/updates/{update_id}/void",
        json={"void_reason": "was recorded by mistake"},
        headers=auth_header(admin_user),
    )
    assert r.status_code == 200
    assert "CURRENT_STATE_NOT_REVERSED" in r.json()["warnings"]
    assert r.json()["update"]["voided_at"] is not None
    # Current state was NOT rewound.
    detail = await client.get(f"{ISSUES}/{iid}", headers=auth_header(admin_user))
    assert detail.json()["status"] == "PENDING"


async def test_void_already_voided_rejected(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    upd = await client.post(
        f"{ISSUES}/{iid}/updates",
        json={"update_date": "2026-07-17", "update_note": "note"},
        headers=auth_header(editor_user),
    )
    update_id = upd.json()["id"]
    body = {"void_reason": "duplicate entry"}
    await client.post(
        f"{ISSUES}/{iid}/updates/{update_id}/void", json=body, headers=auth_header(admin_user)
    )
    r2 = await client.post(
        f"{ISSUES}/{iid}/updates/{update_id}/void", json=body, headers=auth_header(admin_user)
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ISSUE_UPDATE_ALREADY_VOIDED"
