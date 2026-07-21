# Concept by MrHan (08974747477)
"""SQLAlchemy declarative base.

Phase 1: base class only — no engine, no session, no connection. Models are
added in Phase 2 and will subclass Base so Alembic autogenerate can see them.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models (Phase 2+)."""
    pass
