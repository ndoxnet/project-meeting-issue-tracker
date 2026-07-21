# Concept by MrHan (08974747477)
"""Example test for the health endpoint.

Phase 1: this documents the intended test shape. It requires the dependencies
from pyproject.toml (fastapi, httpx). Do NOT run it on the VPS in Phase 1 — run
it on a developer machine where dependencies are installed.
"""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_ok() -> None:
    # Imported inside the test so collection does not fail if deps are absent
    # in an environment where the suite is intentionally not run.
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "project-meeting-issue-tracker-api"
