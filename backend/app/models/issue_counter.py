# Concept by MrHan (08974747477)
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IssueCounter(Base):
    """Per-year sequence backing transaction-safe issue codes (ADR-011).

    The row for a year is locked (SELECT ... FOR UPDATE on PostgreSQL) while the
    counter is incremented, so concurrent issue creation cannot mint duplicate
    numbers. ``issues.issue_code`` UNIQUE is the final guard.
    """

    __tablename__ = "issue_counters"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
