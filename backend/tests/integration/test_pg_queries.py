# Concept by MrHan (08974747477)
"""Dashboard, CSV, attachment, and case-normalization behavior on PostgreSQL —
proves no SQLite-only SQL leaks into production queries."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.timezone import local_today
from tests.conftest import auth_header
from tests.integration.conftest import issue_payload

pytestmark = [pytest.mark.integration, pytest.mark.postgresql, pytest.mark.asyncio]
ISSUES = "/api/v1/issues"
DASH = "/api/v1/dashboard"
USERS = "/api/v1/users"


async def _create(client, hdr, category, *, raised, due=None, title="Issue"):
    payload = issue_payload(category.id, title=title, raised_date=raised.isoformat())
    if due is not None:
        payload["due_date"] = due.isoformat()
    r = await client.post(ISSUES, json=payload, headers=hdr)
    assert r.status_code == 201, r.text
    return r.json()["issue"]["id"]


async def test_dashboard_overdue_stagnant_dueweek(pg_client, admin_user, category) -> None:
    hdr = auth_header(admin_user)
    today = local_today()
    await _create(
        pg_client,
        hdr,
        category,
        raised=today - timedelta(days=40),
        due=today - timedelta(days=1),
        title="Overdue",
    )
    await _create(
        pg_client, hdr, category, raised=today - timedelta(days=40), due=today, title="DueToday"
    )
    await _create(pg_client, hdr, category, raised=today - timedelta(days=30), title="Stale")
    await _create(
        pg_client,
        hdr,
        category,
        raised=today - timedelta(days=1),
        due=today + timedelta(days=3),
        title="DueSoon",
    )

    overdue = await pg_client.get(f"{DASH}/overdue", headers=hdr)
    otitles = [i["title"] for i in overdue.json()]
    assert "Overdue" in otitles and "DueToday" not in otitles  # due today is not overdue

    stagnant = await pg_client.get(f"{DASH}/stagnant", headers=hdr)
    assert "Stale" in [i["title"] for i in stagnant.json()]

    week = await pg_client.get(f"{DASH}/due-this-week", headers=hdr)
    assert "DueSoon" in [i["title"] for i in week.json()]

    summary = await pg_client.get(f"{DASH}/summary", headers=hdr)
    assert summary.json()["overdue_count"] >= 1
    assert summary.json()["stagnant_count"] >= 1


async def test_dashboard_groupings_and_trend(pg_client, admin_user, category) -> None:
    hdr = auth_header(admin_user)
    today = local_today()
    await _create(pg_client, hdr, category, raised=today, title="Grp")
    by_cat = await pg_client.get(f"{DASH}/by-category", headers=hdr)
    assert any(row["label"] == "Engineering" for row in by_cat.json())
    trend = await pg_client.get(f"{DASH}/opened-vs-closed?months=6", headers=hdr)
    assert len(trend.json()) == 6


async def test_csv_export_and_formula_escape(pg_client, admin_user, category) -> None:
    hdr = auth_header(admin_user)
    today = local_today()
    await _create(pg_client, hdr, category, raised=today, title="=DANGER()")
    r = await pg_client.get("/api/v1/reports/issues.csv", headers=hdr)
    assert r.status_code == 200
    text = r.content.decode("utf-8-sig")
    assert "'=DANGER()" in text  # formula-injection escaped


async def test_csv_row_cap(pg_client, admin_user, category, monkeypatch) -> None:
    hdr = auth_header(admin_user)
    today = local_today()
    for i in range(3):
        await _create(pg_client, hdr, category, raised=today, title=f"row{i}")
    monkeypatch.setattr("app.services.report.EXPORT_MAX_ROWS", 2)
    r = await pg_client.get("/api/v1/reports/issues.csv", headers=hdr)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EXPORT_LIMIT_EXCEEDED"


async def test_attachment_upload_and_remove(pg_client, admin_user, editor_user, category) -> None:
    hdr_e = auth_header(editor_user)
    hdr_a = auth_header(admin_user)
    created = await pg_client.post(ISSUES, json=issue_payload(category.id), headers=hdr_e)
    iid = created.json()["issue"]["id"]
    pdf = b"%PDF-1.4\n%%EOF\n"
    up = await pg_client.post(
        f"{ISSUES}/{iid}/attachments",
        files={"file": ("d.pdf", pdf, "application/pdf")},
        headers=hdr_e,
    )
    assert up.status_code == 201
    aid = up.json()["id"]
    assert up.json()["checksum_sha256"]
    # Download works, then admin soft-removes, then download 404.
    dl = await pg_client.get(f"{ISSUES}/{iid}/attachments/{aid}/download", headers=hdr_e)
    assert dl.status_code == 200 and dl.content == pdf
    rm = await pg_client.post(f"{ISSUES}/{iid}/attachments/{aid}/remove", headers=hdr_a)
    assert rm.status_code == 200
    dl2 = await pg_client.get(f"{ISSUES}/{iid}/attachments/{aid}/download", headers=hdr_e)
    assert dl2.status_code == 404


async def test_case_insensitive_email_username(pg_client, admin_user) -> None:
    hdr = auth_header(admin_user)
    base = {
        "full_name": "P One",
        "email": "Mixed@Case.com",
        "username": "MixedUser",
        "role": "EDITOR",
        "password": "BrandNewPass12",
    }
    r1 = await pg_client.post(USERS, json=base, headers=hdr)
    assert r1.status_code == 201
    # Different case -> normalized -> duplicate rejected by the service.
    dup_email = {**base, "username": "otheruser", "email": "mixed@case.com"}
    r2 = await pg_client.post(USERS, json=dup_email, headers=hdr)
    assert r2.status_code == 409
    dup_user = {**base, "email": "new@example.com", "username": "mixeduser"}
    r3 = await pg_client.post(USERS, json=dup_user, headers=hdr)
    assert r3.status_code == 409
