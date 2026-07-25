# Changelog

> Concept by MrHan (08974747477)
All notable changes to this project are documented here.

## [unreleased] — Phase 2C.3 — Attachments, CSV Export, and Monitoring Views
### Added (frontend; validated via GitHub Actions, not on the VPS)
- **Issue attachments** (`features/attachments/`): list (all roles), upload
  (Editor/Admin, non-archived), download, and remove (Admin, confirm dialog),
  wired into the issue detail page. Uploads run a usability pre-check for size
  (10 MB, mirrors `ATTACHMENT_MAX_MB`) and type (PDF/JPEG/PNG); the backend stays
  authoritative. The three rejection codes — `ATTACHMENT_TOO_LARGE` (413),
  `ATTACHMENT_TYPE_NOT_ALLOWED` (415), `ATTACHMENT_CONTENT_MISMATCH` (415) — are
  surfaced distinctly.
- **CSV export** (`features/reports/ExportCsvButton`, `api/reports.ts`): exports
  the register reusing the active server-side filters exactly; no pagination/sort
  is sent (the contract exposes none). `EXPORT_LIMIT_EXCEEDED` is surfaced clearly.
  Available on the Issue Register and a new **Reports** page (replaces the placeholder).
- **Monitoring views** (`pages/tracker/MonitoringPage`): dedicated Overdue /
  Stagnant / Due-this-week lists backed by the `dashboard_{overdue,stagnant,
  due_this_week}` endpoints (server-side logic; never recomputed in the browser),
  reachable from the dashboard KPI cards.
- **Dashboard analytics** (`features/dashboard/`): by-category and
  by-responsible-party distributions (CSS bars) and an opened-vs-closed trend
  (accessible `<table>`, period 6/12/24 months) — **no chart library**; every
  value is readable as text, never bar length or color alone.
- **Downloads** (`lib/download.ts`, `apiClient.download`): authenticated blob
  responses, `Content-Disposition` filename parsing + sanitization with a
  deterministic fallback, and object URLs always revoked. Blobs/object URLs are
  never stored in the query cache.
- **Toasts** (`components/feedback/ToastProvider`): accessible live regions
  (status/alert), auto-dismiss, de-duplicated; supplement — never replace —
  inline form/mutation errors.
- **Tests:** attachments (list/empty/upload-validation/upload/role-gating/
  download-revoke/remove), CSV export (filters forwarded, limit-exceeded),
  monitoring (list/empty/invalid-redirect), analytics (labels+values), toasts.
### Notes
- **Audit** screen remains a documented placeholder: the frozen v1 contract
  exposes no `GET /audit-logs` endpoint. A future read-only audit contract is
  tracked separately; no backend endpoint was added in this frontend phase.
- Users/Settings/master-data admin remain deferred (Phase 2C.4). No backend/DB
  change. No npm run on the VPS.

## [unreleased] — Phase 2C.2 — Authenticated Meeting Issue Tracker Core UI (PASS)
> Frontend Validation green on commit `0c08136`; recorded as PASS.
### Added (frontend; validated via GitHub Actions, not on the VPS)
- **Typed API layer** derived from the generated OpenAPI schema: `api/types.ts`
  (component aliases), `api/{issues,meetings,dashboard,masterdata}.ts` (fetchers +
  React Query hooks), `api/queryKeys.ts`. Mutations invalidate issue/dashboard caches.
- **Pages:** dashboard (real `/dashboard/summary` KPIs + recent issues/meetings),
  meetings list + detail (occurrences + their issues), issues list (URL-synced
  server-side filters + pagination), issue detail (fields + follow-up timeline +
  lifecycle actions), issue create (`POST /issues`), issue edit (diff-based
  `PATCH`, change-reason gating for PIC/due).
- **Lifecycle actions** (Editor/Admin, non-archived): change status / close /
  reopen / add follow-up, gated by an ADR-012 mirror (`features/issues/lifecycle.ts`).
- **Reusable UI:** StatusBadge, PriorityBadge, StatCard, Pagination, Modal,
  Field/Select/TextInput/TextArea, PageHeader, DataState; `lib/dates.ts`
  (date-only vs timestamp handling).
- **Tests:** Vitest + RTL + MSW for issues list/detail/create/edit, meetings
  list/detail, dashboard landing, filter→API, and role gating.
### Notes
- Contract mapping documented (meetings = occurrences; owner ≈ PIC; history =
  issue-updates timeline); no non-contract fields invented. Reports/Users/Audit/
  Settings remain placeholders. No backend/DB change. No npm run on the VPS.

## [unreleased] — Phase 2C.1.5A — Off-VPS Frontend Validation via GitHub Actions
### Added (CI config + docs only — no npm run on the VPS)
- `.github/workflows/frontend-bootstrap-validation.yml` — manual, read-only,
  Node 22, ubuntu-24.04: `npm install` → `generate:api` → lint → typecheck →
  test ×2 → build → source-map check → secret scan → `npm audit`; uploads ONLY
  `package-lock.json` + generated `schema.ts` as artifacts (7-day retention).
- `.github/workflows/frontend-validation.yml.template` — permanent `npm ci` +
  `check:api` workflow, inert until renamed to `.yml` (after the lockfile exists).
- `docs/FRONTEND_CI_BOOTSTRAP.md` — operator procedure (artifact route + dev-machine
  alternative); `.nvmrc` (22) + `engines` in `package.json`.
### Status
- Production VPS validation correctly remained blocked (NO-GO on VPS). Frontend
  runtime is **still unvalidated** until the bootstrap workflow is green and the
  lockfile + real generated types are committed. **Phase 2C.2 remains blocked**
  until the permanent CI passes. No backend/DB/service change.

## [0.3.0-frontend] — Phase 2C.1 — Frontend Auth, API Client, Guards, Shell
### Added (frontend scaffold — runtime validation pending off-VPS)
- **API layer:** native-`fetch` typed client (bearer, JSON/blob/text/void/multipart,
  AbortSignal, 401 handler), normalized `ApiError` (code/status/requestId),
  TanStack Query client (retry ≤1, no mutation retry, cache-clear on logout).
- **Auth (ADR-017):** memory-only token store (no web storage/cookies),
  `AuthProvider` context (`status/user/login/logout/refreshCurrentUser/hasRole`;
  token never exposed), login/logout/`/auth/me` flows, 401 teardown.
- **Routing:** `ProtectedRoute` + `RoleRoute` guards; role-gated sidebar
  navigation; login/forbidden/not-found pages; `/app/*` placeholder pages (no fake
  data); responsive `AppShell` (sidebar + mobile drawer + top bar).
- **Types (ADR-019):** generated `src/api/generated/schema.ts` from OpenAPI +
  readable aliases in `src/api/types.ts`; `check:api` drift guard.
- **Tests:** Vitest + RTL + MSW suites for token store, API client, login flow,
  route/role guards, navigation, logout, and open-redirect prevention.
- **Config/docs:** pinned `package.json`, `.env.example`, Vite proxy/Vitest config,
  ESLint (blocks localStorage/sessionStorage), design tokens; reviewed
  Dockerfile (`npm ci`) + nginx (caching, no autoindex, request-id passthrough);
  `FRONTEND_ARCHITECTURE.md`, `FRONTEND_SECURITY.md`, ADR-018/019.
### Notes
- **Production-VPS branch:** no `npm install`/build/test/`openapi-typescript` were
  run here (ADR-004). The lockfile, real generated types, `lint`/`typecheck`/`test`/
  `build`, and `check:api` are **pending off-VPS**. No backend/business change; no
  production service touched.

## [0.2.0-contract] — Phase 2B.6 — Frozen v1 API Contract
### Added
- **OpenAPI artifacts:** `docs/api/openapi.json` + `.yaml`, generated by
  `backend/scripts/export_openapi.py` (no DB, deterministic; `make openapi-export`).
- **Stable operation IDs** on all 63 operations (readable, domain-prefixed, unique)
  and canonical tags with descriptions; custom OpenAPI injects the error-envelope
  models; app metadata (summary/description/contact/license/dev servers).
- **API docs (`docs/api/`):** ENDPOINTS, AUTHORIZATION, RESPONSE_CONVENTIONS,
  ERROR_CODES, FIELD_SEMANTICS, FILTERS, DASHBOARD, ATTACHMENTS, FRONTEND_HANDOFF,
  COMPATIBILITY_POLICY. ADR-017 (memory-only access token for the frontend MVP).
- **Contract tests** (`tests/contract/`, 24): schema validity, operation-ID
  uniqueness/convention, security (only login/health/ping public; 60 protected),
  error/pagination models, no internal-field exposure, and a **stale-schema drift
  guard** against the committed spec.
- **Makefile:** `openapi-export`, `openapi-check`, `contract-test`,
  `frontend-types-generate` (off-VPS only); `frontend/src/api/generated/` placeholder.
### Notes
- No business logic changed; source edits were limited to OpenAPI metadata,
  operation IDs, and two request-schema examples. Frontend not started (Phase 2C).

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
