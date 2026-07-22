# Concept by MrHan (08974747477)
"""Centralized date/time helpers.

Timestamps are stored in UTC. "Today", "overdue", and "due this week" are computed
against the LOCAL date derived from DISPLAY_TIMEZONE (ADR-007), so they match the
user's calendar day.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.core.config import get_settings


def now_utc() -> datetime:
    return datetime.now(UTC)


def local_today() -> date:
    """Current date in the configured display timezone."""
    tz = get_settings().display_tzinfo
    return datetime.now(tz).date()


def due_this_week_bounds(today: date | None = None) -> tuple[date, date]:
    """Inclusive window for 'due this week': today .. today + 7 days.

    Documented choice (docs/USER_FLOWS.md): today through today+7 inclusive.
    """
    t = today or local_today()
    return t, t + timedelta(days=7)


def stagnant_before(days: int, today: date | None = None) -> date:
    """The cutoff date; last activity strictly older than this is stagnant."""
    t = today or local_today()
    return t - timedelta(days=days)
