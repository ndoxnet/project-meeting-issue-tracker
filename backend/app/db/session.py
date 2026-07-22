# Concept by MrHan (08974747477)
"""Async database engine and session management.

The engine is created lazily from settings (not at import time) so importing the
app never opens a connection. Provides a FastAPI dependency that yields a session,
commits on success, rolls back on error, and always closes.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, creating it on first use."""
    global _engine
    if _engine is None:
        settings = get_settings()
        kwargs: dict = {
            "echo": False,  # never echo SQL (avoids leaking data/credentials)
            "pool_pre_ping": True,
        }
        # Conservative pool for the resource-constrained VPS (Phase 2B.5). SQLite
        # (tests) uses a non-queue pool, so these options don't apply there.
        if settings.DATABASE_URL.startswith("postgresql"):
            kwargs.update(
                pool_size=5,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1800,
            )
        _engine = create_async_engine(settings.DATABASE_URL, **kwargs)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yield a session, rollback on error, always close.

    Endpoints/services are responsible for calling ``await session.commit()``
    at their transaction boundary; this dependency guarantees cleanup.
    """
    sessionmaker = get_sessionmaker()
    session = sessionmaker()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def dispose_engine() -> None:
    """Dispose the engine (used on shutdown and in test teardown)."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None
