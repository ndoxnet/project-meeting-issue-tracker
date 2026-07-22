# Concept by MrHan (08974747477)
from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    open_count: int
    in_progress_count: int
    pending_count: int
    reopened_count: int
    overdue_count: int
    stagnant_count: int
    due_this_week_count: int
    closed_this_month_count: int
    total_active_count: int


class CountByLabel(BaseModel):
    label: str
    count: int


class MonthlyTrendPoint(BaseModel):
    month: str  # YYYY-MM
    opened: int
    closed: int
