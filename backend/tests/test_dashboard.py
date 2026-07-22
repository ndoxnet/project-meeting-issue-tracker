# Concept by MrHan (08974747477)
from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.timezone import local_today
from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"
DASH = "/api/v1/dashboard"


async def _create(client, user, category, *, raised, due=None, title="Issue"):
    payload = issue_payload(category.id, title=title, raised_date=raised.isoformat())
    if due is not None:
        payload["due_date"] = due.isoformat()
    r = await client.post(ISSUES, json=payload, headers=auth_header(user))
    assert r.status_code == 201, r.text
    return r.json()["issue"]["id"]


async def test_overdue_and_due_today_boundary(client, admin_user, category) -> None:
    today = local_today()
    await _create(
        client,
        admin_user,
        category,
        raised=today - timedelta(days=40),
        due=today - timedelta(days=1),
        title="Overdue one",
    )
    await _create(
        client,
        admin_user,
        category,
        raised=today - timedelta(days=40),
        due=today,
        title="Due today",
    )
    r = await client.get(f"{DASH}/overdue", headers=auth_header(admin_user))
    titles = [i["title"] for i in r.json()]
    assert "Overdue one" in titles
    # Due exactly today is NOT overdue.
    assert "Due today" not in titles


async def test_stagnant_uses_raised_fallback(client, admin_user, category) -> None:
    today = local_today()
    # Raised 30 days ago, no follow-up => stagnant (threshold 7).
    await _create(
        client, admin_user, category, raised=today - timedelta(days=30), title="Old stale"
    )
    # Raised today => not stagnant.
    await _create(client, admin_user, category, raised=today, title="Fresh one")
    r = await client.get(f"{DASH}/stagnant", headers=auth_header(admin_user))
    titles = [i["title"] for i in r.json()]
    assert "Old stale" in titles
    assert "Fresh one" not in titles


async def test_due_this_week(client, admin_user, category) -> None:
    today = local_today()
    await _create(
        client,
        admin_user,
        category,
        raised=today - timedelta(days=1),
        due=today + timedelta(days=3),
        title="Due soon",
    )
    await _create(
        client,
        admin_user,
        category,
        raised=today - timedelta(days=1),
        due=today + timedelta(days=20),
        title="Due later",
    )
    r = await client.get(f"{DASH}/due-this-week", headers=auth_header(admin_user))
    titles = [i["title"] for i in r.json()]
    assert "Due soon" in titles
    assert "Due later" not in titles


async def test_summary_excludes_archived(client, admin_user, category) -> None:
    today = local_today()
    iid = await _create(client, admin_user, category, raised=today, title="To archive")
    before = (await client.get(f"{DASH}/summary", headers=auth_header(admin_user))).json()
    await client.post(
        f"{ISSUES}/{iid}/archive", json={"reason": "mistake"}, headers=auth_header(admin_user)
    )
    after = (await client.get(f"{DASH}/summary", headers=auth_header(admin_user))).json()
    assert after["total_active_count"] == before["total_active_count"] - 1


async def test_closed_this_month_and_trend(client, admin_user, category) -> None:
    today = local_today()
    iid = await _create(
        client, admin_user, category, raised=today - timedelta(days=5), title="Close me"
    )
    await client.post(
        f"{ISSUES}/{iid}/close",
        json={"closure_note": "done", "closed_date": today.isoformat()},
        headers=auth_header(admin_user),
    )
    summary = (await client.get(f"{DASH}/summary", headers=auth_header(admin_user))).json()
    assert summary["closed_this_month_count"] >= 1
    trend = await client.get(f"{DASH}/opened-vs-closed?months=3", headers=auth_header(admin_user))
    assert len(trend.json()) == 3
    assert sum(p["closed"] for p in trend.json()) >= 1


async def test_viewer_can_read_dashboard(client, viewer_user) -> None:
    r = await client.get(f"{DASH}/summary", headers=auth_header(viewer_user))
    assert r.status_code == 200


async def test_by_category_grouping(client, admin_user, category) -> None:
    today = local_today()
    await _create(client, admin_user, category, raised=today, title="Grouped")
    r = await client.get(f"{DASH}/by-category", headers=auth_header(admin_user))
    labels = {row["label"]: row["count"] for row in r.json()}
    assert labels.get("Engineering", 0) >= 1
