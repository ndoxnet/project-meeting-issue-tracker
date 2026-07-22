# Changelog

> Concept by MrHan (08974747477)
All notable changes to this project are documented here.

## [0.3.1] — Phase 2B.5 — PostgreSQL Integration & Concurrency Validation
### Fixed
- **Issue-code concurrency (critical):** replaced the counter's `SELECT … FOR
  UPDATE` (which locks nothing when the year's row doesn't exist yet, letting the
  first-of-year concurrent creators collide) with an **atomic upsert**
  (`INSERT … ON CONFLICT (year) DO UPDATE … RETURNING`). Proven with 20 and 50
  concurrent creates → unique, contiguous codes, no duplicates (ADR-011 updated).
  Code-only fix; no migration change.
### Added
- **Pessimistic row locking (ADR-016):** state transitions (metadata/status/close/
  reopen/archive/restore/follow-up) take `SELECT … FOR UPDATE` on the issue row, so
  concurrent lifecycle ops serialize (double-close → one success + one
  `ISSUE_ALREADY_CLOSED`).
- **Conservative production pool** for PostgreSQL: pool_size 5 / overflow 5 /
  timeout 30 / recycle 1800 / pre_ping; `echo=False`.
- **34 PostgreSQL integration tests** (`pytest -m postgresql`): full Alembic
  upgrade/downgrade/re-upgrade + parity, JSONB/INET types, DB-level check/unique/FK
  constraints, concurrent code generation (20 & 50), year partitioning, lifecycle
  races, transaction-atomicity fault injection, dashboard/CSV/attachment queries,
  case-insensitive normalization — all against an isolated, tmpfs, loopback-only
  container. Test transport uses `raise_app_exceptions=False` so 500s are asserted.
### Validation
- Existing 134 SQLite tests still pass; ruff + mypy clean; test container cleaned up
  and container count returned to baseline; no existing service touched.

## [0.3.0] — Phase 2B — Issue Lifecycle, History, Attachments, Dashboard, Export
### Added
- **Issue codes:** `issue_counters` table (11th table) + transaction-safe
  `ISS-YYYY-NNNN` generation with row locking (ADR-011). Migration `bbba43c5c105`.
- **Issue APIs:** list (rich filters, safe sort allow-list, pagination, search),
  create (with duplicate warning), detail, metadata PATCH, status change, close,
  reopen, archive, restore.
- **Lifecycle:** central state machine (ADR-012); every transition writes an
  append-only `issue_update` + audit, atomically.
- **Follow-up history:** append-only updates with status/due/PIC before-after
  capture; Admin void without state rewind (ADR-013, `CURRENT_STATE_NOT_REVERSED`).
- **Attachments:** secure upload (magic-byte sniff, size cap, filename sanitize,
  random stored name, SHA-256, path-traversal-safe), authorized download
  (attachment disposition), soft remove (ADR-014).
- **Dashboard:** summary, overdue, stagnant, due-this-week, recently-updated,
  by-category, by-responsible-party, opened-vs-closed (ADR-015).
- **Export:** filtered `issues.csv` with UTF-8 BOM, formula-injection escaping,
  10k row cap, audited (filters + count, never the body).
- 5 composite indexes on `issues`; new domain error codes; 5 ADRs (011–015).
- ~66 new tests (134 total passing; 3 PostgreSQL integration tests skipped).

### Limitations (documented)
- Concurrency/row-lock behavior proven only on PostgreSQL integration tests
  (pending, `pytest -m postgresql`); SQLite validates logic, not concurrency.
- Attachment sniffing is signature-based (no deep parsing / AV).
- Notifications, frontend, deployment → later phases.

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
