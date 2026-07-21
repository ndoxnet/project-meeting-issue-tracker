# Concept by MrHan (08974747477)
"""Master-data service: categories, responsible parties, meetings, occurrences,
settings. Uniqueness, no hard delete (activate/deactivate), and audit on change."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.errors import ConflictError, NotFoundError
from app.models.app_setting import AppSetting
from app.models.category import Category
from app.models.meeting import Meeting, MeetingOccurrence
from app.models.responsible_party import ResponsibleParty
from app.models.user import User
from app.repositories import masterdata as repo
from app.schemas.masterdata import (
    MeetingOccurrenceCreate,
    MeetingOccurrenceUpdate,
    NamedCreate,
    NamedUpdate,
)
from app.services.audit import record_audit

type NamedAny = Category | ResponsibleParty | Meeting


def _named_public(obj: NamedAny) -> dict:
    return {
        "id": str(obj.id),
        "name": obj.name,
        "description": obj.description,
        "is_active": obj.is_active,
    }


async def create_named[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession,
    model: type[M],
    *,
    entity_type: str,
    data: NamedCreate,
    actor: User,
    ctx: RequestContext,
) -> M:
    if await repo.get_named_by_name(session, model, data.name):
        raise ConflictError(f"{entity_type} name already exists")
    obj = model(name=data.name.strip(), description=data.description, is_active=True)
    session.add(obj)
    await session.flush()
    record_audit(
        session,
        action=f"{entity_type}.create",
        entity_type=entity_type,
        entity_id=obj.id,
        actor_user_id=actor.id,
        after=_named_public(obj),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_named[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession,
    model: type[M],
    *,
    entity_type: str,
    obj_id: uuid.UUID,
    data: NamedUpdate,
    actor: User,
    ctx: RequestContext,
) -> M:
    obj = await repo.get_named(session, model, obj_id)
    if obj is None:
        raise NotFoundError(f"{entity_type} not found")
    before = _named_public(obj)
    if data.name is not None and data.name.strip().lower() != obj.name.lower():
        clash = await repo.get_named_by_name(session, model, data.name)
        if clash and clash.id != obj.id:
            raise ConflictError(f"{entity_type} name already exists")
        obj.name = data.name.strip()
    if data.description is not None:
        obj.description = data.description
    record_audit(
        session,
        action=f"{entity_type}.update",
        entity_type=entity_type,
        entity_id=obj.id,
        actor_user_id=actor.id,
        before=before,
        after=_named_public(obj),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(obj)
    return obj


async def set_named_active[M: (Category, ResponsibleParty, Meeting)](
    session: AsyncSession,
    model: type[M],
    *,
    entity_type: str,
    obj_id: uuid.UUID,
    active: bool,
    actor: User,
    ctx: RequestContext,
) -> M:
    obj = await repo.get_named(session, model, obj_id)
    if obj is None:
        raise NotFoundError(f"{entity_type} not found")
    before = _named_public(obj)
    obj.is_active = active
    record_audit(
        session,
        action=f"{entity_type}." + ("activate" if active else "deactivate"),
        entity_type=entity_type,
        entity_id=obj.id,
        actor_user_id=actor.id,
        before=before,
        after=_named_public(obj),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(obj)
    return obj


# ---- Meeting occurrences ----
def _occ_public(o: MeetingOccurrence) -> dict:
    return {
        "id": str(o.id),
        "meeting_id": str(o.meeting_id),
        "meeting_date": o.meeting_date.isoformat(),
        "meeting_number": o.meeting_number,
        "reference_number": o.reference_number,
    }


async def create_occurrence(
    session: AsyncSession,
    *,
    data: MeetingOccurrenceCreate,
    actor: User,
    ctx: RequestContext,
) -> MeetingOccurrence:
    meeting = await repo.get_named(session, Meeting, data.meeting_id)
    if meeting is None:
        raise NotFoundError("Meeting not found")
    occ = MeetingOccurrence(
        meeting_id=data.meeting_id,
        meeting_date=data.meeting_date,
        meeting_number=data.meeting_number,
        reference_number=data.reference_number,
        agenda=data.agenda,
        minutes_link=data.minutes_link,
        notes=data.notes,
        created_by=actor.id,
    )
    session.add(occ)
    await session.flush()
    record_audit(
        session,
        action="meeting_occurrence.create",
        entity_type="meeting_occurrence",
        entity_id=occ.id,
        actor_user_id=actor.id,
        after=_occ_public(occ),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(occ)
    return occ


async def update_occurrence(
    session: AsyncSession,
    *,
    occ_id: uuid.UUID,
    data: MeetingOccurrenceUpdate,
    actor: User,
    ctx: RequestContext,
) -> MeetingOccurrence:
    occ = await repo.get_occurrence(session, occ_id)
    if occ is None:
        raise NotFoundError("Meeting occurrence not found")
    before = _occ_public(occ)
    for field in (
        "meeting_date",
        "meeting_number",
        "reference_number",
        "agenda",
        "minutes_link",
        "notes",
    ):
        val = getattr(data, field)
        if val is not None:
            setattr(occ, field, val)
    record_audit(
        session,
        action="meeting_occurrence.update",
        entity_type="meeting_occurrence",
        entity_id=occ.id,
        actor_user_id=actor.id,
        before=before,
        after=_occ_public(occ),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(occ)
    return occ


# ---- App settings ----
async def update_setting(
    session: AsyncSession,
    *,
    key: str,
    value: Any,
    actor: User,
    ctx: RequestContext,
) -> AppSetting:
    setting = await repo.get_setting(session, key)
    if setting is None:
        raise NotFoundError("Setting not found")
    before = {"key": setting.key, "value": setting.value}
    setting.value = value
    setting.updated_by = actor.id
    record_audit(
        session,
        action="setting.update",
        entity_type="app_setting",
        entity_id=None,
        actor_user_id=actor.id,
        before=before,
        after={"key": key, "value": value},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(setting)
    return setting
