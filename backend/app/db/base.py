# Concept by MrHan (08974747477)
"""SQLAlchemy declarative base, naming convention, and common mixins.

The naming convention produces stable, predictable constraint/index names so
Alembic autogenerate output is deterministic across runs.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDPKMixin:
    """UUID primary key. Portable: native UUID on PostgreSQL, CHAR on others."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """created_at / updated_at, timezone-aware, UTC via DB server time."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class CreatedAtMixin:
    """created_at only — for append-only tables that must never mutate rows."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
