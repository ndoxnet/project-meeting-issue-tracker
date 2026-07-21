# Changelog

> Concept by MrHan (08974747477)
All notable changes to this project are documented here.

## [0.1.0] — Phase 1 — Architecture & Skeleton
### Added
- Architecture document, ERD, and data dictionary (`docs/`).
- 7 Architecture Decision Records (`docs/ADR/`).
- Repository structure (backend, frontend, deployment, docs).
- Backend skeleton: FastAPI app with `/health` and `/api/ping`, Pydantic settings,
  SQLAlchemy declarative base, Alembic scaffold, example health test.
- Frontend skeleton: React + TS + Vite + Tailwind app shell, sidebar navigation,
  route placeholders for all MVP pages, API client, type placeholders.
- Dockerfiles (backend non-root; frontend multi-stage, build off-VPS).
- `docker-compose.yml` (postgres/backend internal-only; frontend `127.0.0.1:5200`).
- `.env.example`, `.gitignore`, `Makefile`, deployment nginx sample, backup script.

### Notes
- No build, no dependency install, no container run, and no migration were
  performed in Phase 1.
- No existing VPS service was modified.

### Next
- Phase 2: models, migrations, authentication, RBAC, issue lifecycle, audit log,
  backend tests.
