# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPKMixin
from app.db.types import INETType, JSONBType


class AuditLog(UUIDPKMixin, Base):
    """Immutable audit record. No update/delete endpoints exist for this table.

    ``actor_user_id`` may be null (failed login / system action). No cascade from
    users — deleting a user must never erase audit history (users are never hard
    deleted anyway).
    """

    __tablename__ = "audit_logs"

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    # Logical reference (no FK) so any entity type can be audited.
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    before_data: Mapped[dict | None] = mapped_column(JSONBType, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSONBType, nullable=True)

    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INETType, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
