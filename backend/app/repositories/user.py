# Concept by MrHan (08974747477)
"""User data access. Thin query helpers over the session — no generic framework."""
from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User


async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def get_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username.strip().lower())
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email.strip().lower())
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_by_login(session: AsyncSession, identifier: str) -> User | None:
    """Look up by username OR email (both stored normalized lowercase)."""
    ident = identifier.strip().lower()
    stmt = select(User).where(or_(User.username == ident, User.email == ident))
    return (await session.execute(stmt)).scalars().first()


async def list_users(
    session: AsyncSession,
    *,
    offset: int,
    limit: int,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    conditions = []
    if search:
        like = f"%{search.strip()}%"
        conditions.append(
            or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.email.ilike(like),
            )
        )
    if is_active is not None:
        conditions.append(User.is_active.is_(is_active))

    base = select(User)
    count_stmt = select(func.count()).select_from(User)
    for c in conditions:
        base = base.where(c)
        count_stmt = count_stmt.where(c)

    total = (await session.execute(count_stmt)).scalar_one()
    rows = (
        await session.execute(
            base.order_by(User.created_at.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return list(rows), int(total)


async def count_active_admins(session: AsyncSession) -> int:
    stmt = (
        select(func.count())
        .select_from(User)
        .where(User.role == UserRole.ADMIN.value, User.is_active.is_(True))
    )
    return int((await session.execute(stmt)).scalar_one())
