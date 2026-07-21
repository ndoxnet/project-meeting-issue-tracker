# Changelog

> Concept by MrHan (08974747477)
All notable changes to this project are documented here.

## [0.2.0] — Phase 2A — Database, Auth, RBAC, Users, Master Data
### Added
- **Database:** async SQLAlchemy 2 engine/session (lazy), naming-convention
  metadata, portable JSONB/INET types, all 10 ORM models, string-backed enums
  with CHECK constraints, and the initial Alembic migration (`0d3d40690d49`).
- **Auth:** Argon2 password hashing (pwdlib, ADR-008); PyJWT HS256 access tokens
  with sub/iat/exp/jti (ADR-009); `get_current_user` / `get_current_active_user`
  / `require_roles` dependencies (DB role is source of truth).
- **Endpoints:** `/api/v1/auth` (login/logout/me), `/api/v1/users` (CRUD +
  activate/deactivate/reset-password), master data (categories, responsible
  parties, meetings, meeting-occurrences, settings).
- **Audit:** foundation with recursive secret redaction; audited login
  success/failure, logout, user and master-data changes. Request-ID middleware.
- **Consistency:** unified error envelope `{error:{code,message,request_id}}`.
- **Scripts:** idempotent `bootstrap_admin` and `seed_master_data`.
- **Tests:** 68 passing (config, passwords, JWT, models/constraints, auth API,
  users API, master data API, audit, redaction, seed). Ruff + mypy clean.
- 3 new ADRs (008 Argon2, 009 PyJWT/HS256, 010 service/repository boundaries).

### Limitations (documented honestly)
- No server-side token revocation; logout = client discards token; no refresh.
- Migration validated on SQLite (upgrade/downgrade + `alembic check` parity);
  PostgreSQL integration migration NOT executed on the VPS.
- Issue business logic, attachments, dashboard, CSV → Phase 2B. Frontend not
  integrated. No production stack was started.

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
