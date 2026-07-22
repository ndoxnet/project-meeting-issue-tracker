# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"


async def _create(client, user, category, **over):
    return await client.post(
        ISSUES, json=issue_payload(category.id, **over), headers=auth_header(user)
    )


async def test_editor_can_create(client, editor_user, category) -> None:
    r = await _create(client, editor_user, category)
    assert r.status_code == 201


async def test_viewer_cannot_create(client, viewer_user, category) -> None:
    r = await _create(client, viewer_user, category)
    assert r.status_code == 403


async def test_create_audited(client, admin_user, category, sessionmaker) -> None:
    await _create(client, admin_user, category)
    async with sessionmaker() as s:
        rows = (
            (await s.execute(select(AuditLog).where(AuditLog.action == "issue.create")))
            .scalars()
            .all()
        )
    assert len(rows) == 1


async def test_due_before_raised_rejected(client, admin_user, category) -> None:
    r = await _create(client, admin_user, category, due_date="2026-07-01")  # raised 2026-07-10
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "DUE_DATE_BEFORE_RAISED_DATE"


async def test_inactive_category_rejected(client, admin_user, inactive_category) -> None:
    r = await client.post(
        ISSUES, json=issue_payload(inactive_category.id), headers=auth_header(admin_user)
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CATEGORY_INACTIVE"


async def test_duplicate_warning(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="Cable tray clash at Pipe Rack")
    r = await _create(client, admin_user, category, title="Cable tray clash at Pipe Rack")
    assert r.status_code == 201
    warnings = r.json()["warnings"]
    assert any(w["code"] == "POSSIBLE_DUPLICATE" for w in warnings)


async def test_get_detail(client, admin_user, category) -> None:
    created = await _create(client, admin_user, category)
    issue_id = created.json()["issue"]["id"]
    r = await client.get(f"{ISSUES}/{issue_id}", headers=auth_header(admin_user))
    assert r.status_code == 200
    assert r.json()["days_open"] >= 0
    assert "category_name" in r.json()


async def test_get_missing_issue_404(client, admin_user, unknown_uuid) -> None:
    r = await client.get(f"{ISSUES}/{unknown_uuid}", headers=auth_header(admin_user))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "ISSUE_NOT_FOUND"


async def test_metadata_update_requires_change_reason_for_due(client, admin_user, category) -> None:
    created = await _create(client, admin_user, category)
    iid = created.json()["issue"]["id"]
    r = await client.patch(
        f"{ISSUES}/{iid}", json={"due_date": "2026-08-01"}, headers=auth_header(admin_user)
    )
    assert r.status_code == 422  # change_reason required


async def test_metadata_update_due_with_reason_records_history(
    client, admin_user, category
) -> None:
    created = await _create(client, admin_user, category)
    iid = created.json()["issue"]["id"]
    r = await client.patch(
        f"{ISSUES}/{iid}",
        json={"due_date": "2026-08-01", "change_reason": "Client extended deadline"},
        headers=auth_header(admin_user),
    )
    assert r.status_code == 200
    updates = await client.get(f"{ISSUES}/{iid}/updates", headers=auth_header(admin_user))
    due_changes = [u for u in updates.json() if u["due_date_after"] == "2026-08-01"]
    assert len(due_changes) == 1


async def test_list_pagination_and_search(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="Alpha unique token")
    await _create(client, admin_user, category, title="Beta other")
    r = await client.get(
        f"{ISSUES}?search=unique&page=1&page_size=10", headers=auth_header(admin_user)
    )
    assert r.status_code == 200
    titles = [i["title"] for i in r.json()["items"]]
    assert any("Alpha" in t for t in titles)
    assert all("Beta" not in t for t in titles)


async def test_sort_allowlist_ignores_unknown_column(client, admin_user, category) -> None:
    await _create(client, admin_user, category)
    r = await client.get(f"{ISSUES}?sort_by=password_hash", headers=auth_header(admin_user))
    # Unknown sort key is ignored (safe default ordering), not an error.
    assert r.status_code == 200
