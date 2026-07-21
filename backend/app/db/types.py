# Concept by MrHan (08974747477)
"""Portable column types.

Production is PostgreSQL (JSONB, INET). Tests use SQLite, which lacks those
types, so we declare cross-dialect variants that degrade cleanly for tests
without weakening the PostgreSQL schema.
"""
from __future__ import annotations

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import INET, JSONB

# JSONB on PostgreSQL, generic JSON elsewhere (e.g. SQLite for tests).
JSONBType = JSON().with_variant(JSONB(), "postgresql")

# INET on PostgreSQL, VARCHAR(45) elsewhere (fits IPv6).
INETType = String(45).with_variant(INET(), "postgresql")
