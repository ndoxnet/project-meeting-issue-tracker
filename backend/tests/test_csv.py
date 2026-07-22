# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"
CSV = "/api/v1/reports/issues.csv"


async def _create(client, user, category, **over):
    r = await client.post(
        ISSUES, json=issue_payload(category.id, **over), headers=auth_header(user)
    )
    return r.json()["issue"]["id"]


async def test_csv_basic(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="Export me")
    r = await client.get(CSV, headers=auth_header(admin_user))
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    body = r.content
    assert body.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM
    text = body.decode("utf-8-sig")
    assert "Issue Code" in text
    assert "Export me" in text
    # Internal columns must not appear.
    assert "password" not in text.lower()
    assert "storage_path" not in text.lower()


async def test_csv_formula_injection_escaped(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="=SUM(A1:A2)")
    r = await client.get(CSV, headers=auth_header(admin_user))
    text = r.content.decode("utf-8-sig")
    # The dangerous title is prefixed with an apostrophe.
    assert "'=SUM(A1:A2)" in text


async def test_csv_filter_honored(client, admin_user, category) -> None:
    await _create(client, admin_user, category, title="KeepUnique")
    await _create(client, admin_user, category, title="DropOther")
    r = await client.get(f"{CSV}?search=KeepUnique", headers=auth_header(admin_user))
    text = r.content.decode("utf-8-sig")
    assert "KeepUnique" in text
    assert "DropOther" not in text


async def test_csv_archived_excluded_by_default(client, admin_user, category) -> None:
    iid = await _create(client, admin_user, category, title="ArchivedRow")
    await client.post(
        f"{ISSUES}/{iid}/archive", json={"reason": "x"}, headers=auth_header(admin_user)
    )
    r = await client.get(CSV, headers=auth_header(admin_user))
    assert "ArchivedRow" not in r.content.decode("utf-8-sig")


async def test_csv_export_audited(client, admin_user, category, sessionmaker) -> None:
    await _create(client, admin_user, category)
    await client.get(f"{CSV}?search=xyz", headers=auth_header(admin_user))
    async with sessionmaker() as s:
        rows = (
            (await s.execute(select(AuditLog).where(AuditLog.action == "report.issue_csv_export")))
            .scalars()
            .all()
        )
    assert len(rows) >= 1
    # Audit stores filters + count, not the CSV body.
    assert "row_count" in (rows[-1].after_data or {})


async def test_viewer_can_export(client, viewer_user) -> None:
    r = await client.get(CSV, headers=auth_header(viewer_user))
    assert r.status_code == 200
