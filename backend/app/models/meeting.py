# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class Meeting(UUIDPKMixin, TimestampMixin, Base):
    """Master meeting TYPE (e.g. 'Weekly Progress Meeting'), not one occurrence."""

    __tablename__ = "meetings"

    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MeetingOccurrence(UUIDPKMixin, TimestampMixin, Base):
    """A single instance of a meeting on a date."""

    __tablename__ = "meeting_occurrences"
    __table_args__ = (
        # Soft duplicate guard (sensible, not over-strict): same type + date +
        # number should be unique. A null meeting_number still allows multiple
        # same-day rows when genuinely needed.
        UniqueConstraint(
            "meeting_id", "meeting_date", "meeting_number", name="occurrence_identity"
        ),
    )

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meetings.id"), nullable=False, index=True
    )
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    meeting_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    agenda: Mapped[str | None] = mapped_column(Text, nullable=True)
    minutes_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
