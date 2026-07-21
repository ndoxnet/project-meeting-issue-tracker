# Backend — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> FastAPI + SQLAlchemy 2 + Alembic + Pydantic 2. **Phase 1 skeleton.**

## Layout
```
app/
  api/v1/            # versioned API (router.py placeholder; endpoints/ in Phase 2)
  api/deps/          # dependency-injection helpers (Phase 2)
  core/config.py     # Pydantic settings (env-driven)
  db/base.py         # SQLAlchemy declarative Base
  models/            # ORM models (Phase 2)
  repositories/      # data-access layer (Phase 2)
  schemas/           # Pydantic request/response models (Phase 2)
  services/          # business logic incl. lifecycle validation (Phase 2)
  middleware/        # request-id, audit context (Phase 2)
  utils/             # helpers (issue-code, timezone) (Phase 2)
  main.py            # FastAPI app + /health
alembic/             # migrations (versions/ empty in Phase 1)
tests/               # pytest (test_health.py example)
scripts/             # create_admin.py (Phase 2)
```

## Local run (developer machine only — never build/run on the VPS in Phase 1)
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

## Endpoints (Phase 2A)
- `GET /health`, `GET /api/ping` — meta (no DB).
- `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`
- `GET|POST /api/v1/users`, `GET|PATCH /api/v1/users/{id}`,
  `POST /api/v1/users/{id}/activate|deactivate|reset-password` (ADMIN)
- `/api/v1/categories`, `/api/v1/responsible-parties`, `/api/v1/meetings`
  (read: any role; write: ADMIN) with `/{id}/activate|deactivate`
- `/api/v1/meeting-occurrences` (read: any; create/update: EDITOR+)
- `/api/v1/settings`, `/api/v1/settings/{key}` (read: any; PATCH: ADMIN)

## Scripts
- `python -m scripts.bootstrap_admin` — idempotent admin from env.
- `python -m scripts.seed_master_data` — idempotent categories/parties/meetings.

## Quality gates (Phase 2A)
- `pytest -q` → 68 passing · `ruff check .` clean · `mypy app` clean.
- Migration `0d3d40690d49` validated on SQLite (upgrade/downgrade + `alembic
  check`); not run on PostgreSQL.

## Notes
- No database connection is opened at import time; the engine is created lazily.
- No dependency lockfile is committed (installs happen off-VPS — ADR-004).
