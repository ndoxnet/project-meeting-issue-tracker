# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"


async def _create(client, admin_user, category, **over):
    resp = await client.post(
        ISSUES, json=issue_payload(category.id, **over), headers=auth_header(admin_user)
    )
    return resp


async def test_first_issue_of_year(client, admin_user, category) -> None:
    resp = await _create(client, admin_user, category)
    assert resp.status_code == 201
    assert resp.json()["issue"]["issue_code"] == "ISS-2026-0001"


async def test_sequential_codes(client, admin_user, category) -> None:
    r1 = await _create(client, admin_user, category, title="A one")
    r2 = await _create(client, admin_user, category, title="B two")
    assert r1.json()["issue"]["issue_code"] == "ISS-2026-0001"
    assert r2.json()["issue"]["issue_code"] == "ISS-2026-0002"


async def test_new_year_resets(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="Y2026", raised_date="2026-03-01")
    r = await _create(client, admin_user, category, title="Y2027", raised_date="2027-01-05")
    assert r.json()["issue"]["issue_code"] == "ISS-2027-0001"


async def test_issue_code_and_status_forced(client, admin_user, category) -> None:
    # Client cannot set status or code; status is always OPEN on create.
    resp = await _create(client, admin_user, category)
    body = resp.json()["issue"]
    assert body["status"] == "OPEN"
    assert body["issue_code"].startswith("ISS-2026-")
