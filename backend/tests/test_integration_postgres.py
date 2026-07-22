# Concept by MrHan (08974747477)
"""PostgreSQL integration tests (NOT run by default).

These require a real, isolated PostgreSQL instance and are skipped unless
INTEGRATION_DATABASE_URL is set. They are the place where concurrency,
row-locking (FOR UPDATE), JSONB/INET, and full migration behavior are proven.

    Run (only against a throwaway DB, never production):
        INTEGRATION_DATABASE_URL=postgresql+asyncpg://... pytest -m postgresql
"""

from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.postgresql]

_URL = os.environ.get("INTEGRATION_DATABASE_URL")
skip = pytest.mark.skipif(
    not _URL, reason="INTEGRATION_DATABASE_URL not set (PostgreSQL integration not run)"
)


@skip
async def test_concurrent_issue_code_generation_is_unique() -> None:
    # Placeholder: spawn concurrent create_issue calls and assert unique codes.
    # Verifies the SELECT ... FOR UPDATE row lock on issue_counters.
    raise NotImplementedError("Implement against a real PostgreSQL instance")


@skip
async def test_jsonb_and_inet_roundtrip() -> None:
    raise NotImplementedError("Implement against a real PostgreSQL instance")


@skip
async def test_full_alembic_upgrade_downgrade_on_postgres() -> None:
    raise NotImplementedError("Implement against a real PostgreSQL instance")
