# Concept by MrHan (08974747477)
"""Fixtures for PostgreSQL integration tests (Phase 2B.5).

These run ONLY when POSTGRES_TEST_DATABASE_URL (or INTEGRATION_DATABASE_URL) is
set and point at an isolated, throwaway PostgreSQL. The schema is expected to be
migrated (alembic upgrade head) beforehand; each test truncates all tables first
so tests are independent. The app's request session (get_db) is overridden to use
the PostgreSQL engine.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.passwords import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.category import Category
from app.models.enums import UserRole
from app.models.meeting import Meeting, MeetingOccurrence
from app.models.responsible_party import ResponsibleParty
from app.models.user import User

PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL") or os.environ.get("INTEGRATION_DATABASE_URL")

# Every test in this package requires a real PostgreSQL.
pytestmark = [pytest.mark.integration, pytest.mark.postgresql]

_skip = pytest.mark.skipif(
    not PG_URL, reason="POSTGRES_TEST_DATABASE_URL not set (PostgreSQL integration)"
)

# Table names to truncate between tests (alembic_version is preserved).
_TABLES = [t.name for t in Base.metadata.sorted_tables]


@pytest_asyncio.fixture
async def pg_engine():
    # Pool sized to hold every concurrent transaction in the concurrency tests
    # (each holds a connection while waiting on the FOR UPDATE counter lock).
    engine = create_async_engine(
        PG_URL,
        pool_size=60,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    # Clean slate before each test.
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {', '.join(_TABLES)} RESTART IDENTITY CASCADE"))
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def pg_sessionmaker(pg_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(pg_engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def pg_session(pg_sessionmaker) -> AsyncIterator[AsyncSession]:
    async with pg_sessionmaker() as s:
        yield s


@pytest_asyncio.fixture
async def pg_client(pg_sessionmaker) -> AsyncIterator[AsyncClient]:
    async def _override() -> AsyncIterator[AsyncSession]:
        session = pg_sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = _override
    # raise_app_exceptions=False so a genuine 500 is returned as a response
    # (matching real deployments) instead of httpx re-raising the app exception.
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://pgtest") as c:
        yield c
    app.dependency_overrides.clear()


async def make_user(
    pg_sessionmaker, *, username: str, role: UserRole, is_active: bool = True
) -> User:
    async with pg_sessionmaker() as s:
        u = User(
            full_name=username.title(),
            email=f"{username}@example.com",
            username=username,
            password_hash=hash_password("ValidPassw0rd!!"),
            role=role.value,
            is_active=is_active,
        )
        s.add(u)
        await s.commit()
        await s.refresh(u)
        return u


@pytest_asyncio.fixture
async def admin_user(pg_sessionmaker) -> User:
    return await make_user(pg_sessionmaker, username="admin", role=UserRole.ADMIN)


@pytest_asyncio.fixture
async def editor_user(pg_sessionmaker) -> User:
    return await make_user(pg_sessionmaker, username="editor", role=UserRole.EDITOR)


@pytest_asyncio.fixture
async def category(pg_sessionmaker) -> Category:
    async with pg_sessionmaker() as s:
        c = Category(name="Engineering", is_active=True)
        s.add(c)
        await s.commit()
        await s.refresh(c)
        return c


@pytest_asyncio.fixture
async def responsible_party(pg_sessionmaker) -> ResponsibleParty:
    async with pg_sessionmaker() as s:
        r = ResponsibleParty(name="Main Contractor", is_active=True)
        s.add(r)
        await s.commit()
        await s.refresh(r)
        return r


@pytest_asyncio.fixture
async def occurrence(pg_sessionmaker, admin_user) -> MeetingOccurrence:
    async with pg_sessionmaker() as s:
        m = Meeting(name="Weekly Progress Meeting", is_active=True)
        s.add(m)
        await s.flush()
        occ = MeetingOccurrence(
            meeting_id=m.id,
            meeting_date=date(2026, 7, 10),
            meeting_number="#14",
            created_by=admin_user.id,
        )
        s.add(occ)
        await s.commit()
        await s.refresh(occ)
        return occ


def issue_payload(category_id, **over) -> dict:
    base = {
        "title": "Manpower shortage at Area 5",
        "description": "Contractor manpower below plan.",
        "category_id": str(category_id),
        "priority": "HIGH",
        "raised_date": "2026-07-10",
    }
    base.update(over)
    return base
