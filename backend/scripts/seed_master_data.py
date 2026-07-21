# Concept by MrHan (08974747477)
"""Idempotent seed for master data (categories, responsible parties, meetings)
and default app settings.

- Does NOT create duplicates (matches by name, case-insensitive).
- Does NOT re-activate an inactive record (leaves explicit admin decisions alone).
- Does NOT run automatically on import — call seed(session) or run as a script.
"""
from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import dispose_engine, get_sessionmaker
from app.models.app_setting import AppSetting
from app.models.category import Category
from app.models.meeting import Meeting
from app.models.responsible_party import ResponsibleParty
from app.repositories import masterdata as repo

CATEGORIES = [
    "Engineering",
    "Procurement",
    "Construction",
    "Mechanical Completion",
    "Commissioning",
    "Contract",
    "Schedule",
    "HSE",
    "Quality",
    "Other",
]

RESPONSIBLE_PARTIES = [
    "Owner",
    "Main Contractor",
    "Subcontractor",
    "Vendor",
    "Consultant",
    "Joint Action",
    "Other",
]

MEETINGS = [
    "Weekly Progress Meeting",
    "Construction Meeting",
    "Engineering Meeting",
    "Procurement Meeting",
    "Mechanical Completion Meeting",
    "Commissioning Meeting",
    "Management Meeting",
]


async def _seed_named(session: AsyncSession, model: type, names: list[str]) -> int:
    created = 0
    for name in names:
        if await repo.get_named_by_name(session, model, name) is None:
            session.add(model(name=name, is_active=True))
            created += 1
    return created


async def _seed_settings(session: AsyncSession) -> int:
    settings = get_settings()
    defaults = {
        "stagnant_days": settings.STAGNANT_DAYS,
        "attachment_max_mb": settings.ATTACHMENT_MAX_MB,
        "attachment_allowed_types": settings.attachment_allowed_types_list,
        "issue_code_prefix": settings.ISSUE_CODE_PREFIX,
        "display_timezone": settings.DISPLAY_TIMEZONE,
    }
    created = 0
    for key, value in defaults.items():
        if await repo.get_setting(session, key) is None:
            session.add(AppSetting(key=key, value=value))
            created += 1
    return created


async def seed(session: AsyncSession) -> dict[str, int]:
    """Idempotently seed all master data in one transaction. Returns counts."""
    counts = {
        "categories": await _seed_named(session, Category, CATEGORIES),
        "responsible_parties": await _seed_named(
            session, ResponsibleParty, RESPONSIBLE_PARTIES
        ),
        "meetings": await _seed_named(session, Meeting, MEETINGS),
        "settings": await _seed_settings(session),
    }
    await session.commit()
    return counts


async def _run() -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        counts = await seed(session)
    print(f"[seed_master_data] created: {counts}")


def main() -> None:  # pragma: no cover
    try:
        asyncio.run(_run())
    finally:
        asyncio.run(dispose_engine())


if __name__ == "__main__":  # pragma: no cover
    main()
