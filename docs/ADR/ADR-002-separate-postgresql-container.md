# ADR-002 — Separate, Dedicated PostgreSQL Container

**Status:** Accepted

## Context
The VPS already runs a PostgreSQL container for the AI-XAUUSD system
(`ai_xauusd_blueprint_v1-postgres`, host port 55432). Project rules forbid
touching that container or its data. Resources are constrained.

## Decision
Run a **dedicated PostgreSQL 16 Alpine container** for the Issue Tracker on the
internal Compose network only, with **no host port mapping**. Use a distinct
named volume (`issue_tracker_postgres_data`) and a distinct database/user.

## Consequences
- Complete isolation from the trading Postgres — no shared credentials, no shared
  schema, no accidental cross-impact.
- The database is unreachable from the host or internet (defense in depth).
- Slightly higher memory footprint than reusing an existing server, mitigated by
  a conservative memory limit (256–384 MB).

## Alternatives Considered
- **Reuse AI-XAUUSD Postgres with a separate database**: rejected — violates the
  "do not touch existing services" rule and couples unrelated systems.
- **SQLite**: rejected — spec mandates PostgreSQL; concurrent writers and `jsonb`
  audit data fit Postgres better.
