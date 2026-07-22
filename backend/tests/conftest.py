# Concept by MrHan (08974747477)
"""Test fixtures.

Environment is configured BEFORE importing the app so strict settings validation
passes and the app uses an in-memory async SQLite database. Each test gets a
fresh schema (StaticPool keeps a single connection so the in-memory DB persists
within a test).
"""

from __future__ import annotations

import os
import tempfile

# --- must run before importing app modules ---
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_INITIAL_PASSWORD", "AdminPassw0rd!!")
# Attachment tests: writable temp storage + a small size cap so limit tests are cheap.
os.environ.setdefault("STORAGE_PATH", tempfile.mkdtemp(prefix="ittest-storage-"))
os.environ.setdefault("ATTACHMENT_MAX_MB", "1")

import uuid  # noqa: E402
from collections.abc import AsyncIterator  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.passwords import hash_password  # noqa: E402
from app.core.tokens import create_access_token  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.meeting import Meeting, MeetingOccurrence  # noqa: E402
from app.models.responsible_party import ResponsibleParty  # noqa: E402
from app.models.user import User  # noqa: E402

get_settings.cache_clear()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def db_session(sessionmaker) -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session


@pytest_asyncio.fixture
async def client(sessionmaker) -> AsyncIterator[AsyncClient]:
    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        session = sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ---- user factory / role fixtures ----
async def make_user(
    sessionmaker,
    *,
    username: str,
    role: UserRole,
    password: str = "ValidPassw0rd!!",
    is_active: bool = True,
    email: str | None = None,
) -> User:
    async with sessionmaker() as session:
        user = User(
            full_name=username.title(),
            email=email or f"{username}@example.com",
            username=username,
            password_hash=hash_password(password),
            role=role.value,
            is_active=is_active,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def auth_header(user: User) -> dict[str, str]:
    token, _ = create_access_token(user_id=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(sessionmaker) -> User:
    return await make_user(sessionmaker, username="admin", role=UserRole.ADMIN)


@pytest_asyncio.fixture
async def editor_user(sessionmaker) -> User:
    return await make_user(sessionmaker, username="editor", role=UserRole.EDITOR)


@pytest_asyncio.fixture
async def viewer_user(sessionmaker) -> User:
    return await make_user(sessionmaker, username="viewer", role=UserRole.VIEWER)


@pytest.fixture
def unknown_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ---- master-data fixtures for issue tests ----
@pytest_asyncio.fixture
async def category(sessionmaker) -> Category:
    async with sessionmaker() as s:
        c = Category(name="Engineering", is_active=True)
        s.add(c)
        await s.commit()
        await s.refresh(c)
        return c


@pytest_asyncio.fixture
async def inactive_category(sessionmaker) -> Category:
    async with sessionmaker() as s:
        c = Category(name="Legacy", is_active=False)
        s.add(c)
        await s.commit()
        await s.refresh(c)
        return c


@pytest_asyncio.fixture
async def responsible_party(sessionmaker) -> ResponsibleParty:
    async with sessionmaker() as s:
        r = ResponsibleParty(name="Main Contractor", is_active=True)
        s.add(r)
        await s.commit()
        await s.refresh(r)
        return r


@pytest_asyncio.fixture
async def occurrence(sessionmaker, admin_user) -> MeetingOccurrence:
    from datetime import date

    async with sessionmaker() as s:
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
