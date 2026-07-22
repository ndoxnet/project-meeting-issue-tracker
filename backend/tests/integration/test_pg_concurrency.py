# Concept by MrHan (08974747477)
"""Concurrency proofs on PostgreSQL: issue-code generation under load, year
partitioning, and lifecycle races serialized by FOR UPDATE row locks (ADR-016)."""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.models.issue_counter import IssueCounter
from tests.conftest import auth_header
from tests.integration.conftest import issue_payload

pytestmark = [pytest.mark.integration, pytest.mark.postgresql, pytest.mark.asyncio]
ISSUES = "/api/v1/issues"


async def _create_many(client, hdr, category, n, *, year="2026", title_prefix="c"):
    async def one(i):
        return await client.post(
            ISSUES,
            json=issue_payload(
                category.id, title=f"{title_prefix}{i}", raised_date=f"{year}-07-10"
            ),
            headers=hdr,
        )

    return await asyncio.gather(*[one(i) for i in range(n)])


async def test_concurrent_issue_code_20(pg_client, pg_sessionmaker, editor_user, category) -> None:
    results = await _create_many(pg_client, auth_header(editor_user), category, 20)
    codes = [r.json()["issue"]["issue_code"] for r in results if r.status_code == 201]
    assert len(codes) == 20, [r.status_code for r in results]
    assert len(set(codes)) == 20  # no duplicates
    numbers = sorted(int(c.rsplit("-", 1)[1]) for c in codes)
    assert numbers == list(range(1, 21))  # contiguous set, no gaps
    async with pg_sessionmaker() as s:
        counter = (
            await s.execute(select(IssueCounter).where(IssueCounter.year == 2026))
        ).scalar_one()
    assert counter.last_number == 20


async def test_concurrent_issue_code_50(pg_client, pg_sessionmaker, editor_user, category) -> None:
    results = await _create_many(pg_client, auth_header(editor_user), category, 50)
    codes = [r.json()["issue"]["issue_code"] for r in results if r.status_code == 201]
    assert len(codes) == 50
    assert len(set(codes)) == 50
    assert sorted(int(c.rsplit("-", 1)[1]) for c in codes) == list(range(1, 51))


async def test_multi_year_counters_independent(
    pg_client, pg_sessionmaker, editor_user, category
) -> None:
    hdr = auth_header(editor_user)
    r2026 = await _create_many(pg_client, hdr, category, 10, year="2026", title_prefix="a")
    r2027 = await _create_many(pg_client, hdr, category, 10, year="2027", title_prefix="b")
    codes26 = {r.json()["issue"]["issue_code"] for r in r2026 if r.status_code == 201}
    codes27 = {r.json()["issue"]["issue_code"] for r in r2027 if r.status_code == 201}
    assert all(c.startswith("ISS-2026-") for c in codes26)
    assert all(c.startswith("ISS-2027-") for c in codes27)
    assert "ISS-2026-0001" in codes26
    assert "ISS-2027-0001" in codes27  # new year restarts at 0001
    async with pg_sessionmaker() as s:
        rows = (await s.execute(select(IssueCounter))).scalars().all()
    per_year = {r.year: r.last_number for r in rows}
    assert per_year[2026] == 10 and per_year[2027] == 10


async def test_double_close_race(pg_client, editor_user, category) -> None:
    hdr = auth_header(editor_user)
    created = await pg_client.post(ISSUES, json=issue_payload(category.id), headers=hdr)
    iid = created.json()["issue"]["id"]
    body = {"closure_note": "done", "closed_date": "2026-08-05"}

    async def close():
        return await pg_client.post(f"{ISSUES}/{iid}/close", json=body, headers=hdr)

    r1, r2 = await asyncio.gather(close(), close())
    statuses = sorted([r1.status_code, r2.status_code])
    # Exactly one closes; the other is rejected as already closed (row lock).
    assert statuses == [200, 409]
    loser = r1 if r1.status_code == 409 else r2
    assert loser.json()["error"]["code"] == "ISSUE_ALREADY_CLOSED"


async def test_concurrent_followups_no_corruption(pg_client, editor_user, category) -> None:
    hdr = auth_header(editor_user)
    created = await pg_client.post(ISSUES, json=issue_payload(category.id), headers=hdr)
    iid = created.json()["issue"]["id"]

    async def follow(note):
        return await pg_client.post(
            f"{ISSUES}/{iid}/updates",
            json={"update_date": "2026-07-17", "update_note": note},
            headers=hdr,
        )

    results = await asyncio.gather(*[follow(f"note {i}") for i in range(10)])
    assert all(r.status_code == 201 for r in results)
    # All follow-ups persisted (10) plus the initial "Issue raised" update = 11.
    updates = await pg_client.get(f"{ISSUES}/{iid}/updates", headers=hdr)
    assert len(updates.json()) == 11
