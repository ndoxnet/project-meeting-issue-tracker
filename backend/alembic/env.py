# Concept by MrHan (08974747477)
"""Alembic migration environment.

Phase 1: scaffolding only — no migrations exist yet and this is not executed on
the VPS. In Phase 2, target_metadata is set to Base.metadata (with models
imported) and DATABASE_URL is read from application settings.
"""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Phase 2 will wire real metadata:
#   from app.db.base import Base
#   from app import models  # noqa: F401  (import models so they register)
#   target_metadata = Base.metadata
target_metadata = None


def _get_url() -> str:
    """Read the DB URL from application settings (env), not from alembic.ini."""
    from app.core.config import get_settings

    return get_settings().DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Phase 2 implements the async engine connection here.
    from sqlalchemy import create_engine

    connectable = create_engine(_get_url().replace("+asyncpg", ""))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
