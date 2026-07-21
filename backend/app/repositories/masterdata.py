# Concept by MrHan (08974747477)
"""Data access for master-data entities (categories, responsible parties,
meetings, meeting occurrences, app settings)."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_setting import AppSetting
from app.models.category import Category
from app.models.meeting import Meeting, MeetingOccurrence
from app.models.responsible_party import ResponsibleParty

# Named master entities share a shape (id, name, description, is_active).
type NamedAny = Category | ResponsibleParty | Meeting


async def get_named[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession, model: type[M], obj_id: uuid.UUID
) -> M | None:
    return await session.get(model, obj_id)


async def get_named_by_name[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession, model: type[M], name: str
) -> M | None:
    stmt = select(model).where(func.lower(model.name) == name.strip().lower())
    return (await session.execute(stmt)).scalars().first()


async def list_named[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession,
    model: type[M],
    *,
    offset: int,
    limit: int,
    is_active: bool | None = None,
    search: str | None = None,
) -> tuple[list[M], int]:
    base = select(model)
    count_stmt = select(func.count()).select_from(model)
    if is_active is not None:
        base = base.where(model.is_active.is_(is_active))
        count_stmt = count_stmt.where(model.is_active.is_(is_active))
    if search:
        like = f"%{search.strip()}%"
        base = base.where(model.name.ilike(like))
        count_stmt = count_stmt.where(model.name.ilike(like))

    total = (await session.execute(count_stmt)).scalar_one()
    rows = (
        await session.execute(base.order_by(model.name.asc()).offset(offset).limit(limit))
    ).scalars().all()
    return list(rows), int(total)


# ---- Meeting occurrences ----
async def get_occurrence(
    session: AsyncSession, occ_id: uuid.UUID
) -> MeetingOccurrence | None:
    return await session.get(MeetingOccurrence, occ_id)


async def list_occurrences(
    session: AsyncSession,
    *,
    offset: int,
    limit: int,
    meeting_id: uuid.UUID | None = None,
) -> tuple[list[MeetingOccurrence], int]:
    base = select(MeetingOccurrence)
    count_stmt = select(func.count()).select_from(MeetingOccurrence)
    if meeting_id is not None:
        base = base.where(MeetingOccurrence.meeting_id == meeting_id)
        count_stmt = count_stmt.where(MeetingOccurrence.meeting_id == meeting_id)

    total = (await session.execute(count_stmt)).scalar_one()
    rows = (
        await session.execute(
            base.order_by(MeetingOccurrence.meeting_date.desc()).offset(offset).limit(limit)
        )
    ).scalars().all()
    return list(rows), int(total)


# ---- App settings ----
async def get_setting(session: AsyncSession, key: str) -> AppSetting | None:
    return await session.get(AppSetting, key)


async def list_settings(session: AsyncSession) -> list[AppSetting]:
    rows = (
        await session.execute(select(AppSetting).order_by(AppSetting.key.asc()))
    ).scalars().all()
    return list(rows)
