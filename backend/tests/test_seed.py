# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.models.category import Category
from scripts.seed_master_data import CATEGORIES, MEETINGS, RESPONSIBLE_PARTIES, seed

pytestmark = pytest.mark.asyncio


async def test_seed_creates_expected_counts(db_session) -> None:
    counts = await seed(db_session)
    assert counts["categories"] == len(CATEGORIES)
    assert counts["responsible_parties"] == len(RESPONSIBLE_PARTIES)
    assert counts["meetings"] == len(MEETINGS)
    assert counts["settings"] == 5


async def test_seed_is_idempotent(db_session) -> None:
    await seed(db_session)
    second = await seed(db_session)
    assert second == {
        "categories": 0,
        "responsible_parties": 0,
        "meetings": 0,
        "settings": 0,
    }
    total = (
        await db_session.execute(select(func.count()).select_from(Category))
    ).scalar_one()
    assert total == len(CATEGORIES)
