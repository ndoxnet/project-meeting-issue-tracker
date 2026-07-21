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

## Endpoints (Phase 1)
- `GET /health` → `{"status":"ok","service":"...","version":"0.1.0"}`
- `GET /api/ping` → `{"message":"pong"}`

## Notes
- No database connection is opened at import or startup in Phase 1.
- No dependency lockfile is committed (installs happen off-VPS — ADR-004).
