# Development Guide — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> Phase 1 is skeleton only. Commands below describe the intended local workflow;
> **dependency install and builds happen on a developer machine, not the VPS.**

## Prerequisites (developer machine)
- Python 3.12, Docker + Compose v2, Node.js LTS (for the frontend, off-VPS).

## Backend (local)
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"     # installs from pyproject.toml (dev machine only)
uvicorn app.main:app --reload --port 8000   # local dev only
```
- Lint: `ruff check .` — Types: `mypy app` — Tests: `pytest -q`.

> Note: on hosts where `python3-venv`/`ensurepip` is unavailable (as on the
> current VPS), create the environment with `virtualenv -p python3.12 .venv`
> (which bundles pip) instead of `python -m venv`.

## Environment for tests
Tests set required env vars in `tests/conftest.py` **before** importing the app
(strict settings validation) and use an in-memory async SQLite database. Run the
suite single-process (no `pytest-xdist`). Argon2 makes the suite ~1 min — expected.

## Migrations (Alembic, async)
```bash
# DATABASE_URL + SECRET_KEY must be set in the environment.
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic check          # verify models match the latest migration
```
The initial migration is `alembic/versions/0d3d40690d49_initial_schema_phase_2a.py`.
It was validated on SQLite (upgrade/downgrade + `alembic check`); it has NOT been
run against PostgreSQL on the VPS.

## Frontend (local, OFF-VPS)
```bash
cd frontend
npm install                 # off-VPS only (ADR-004); creates & commits package-lock.json
npm run generate:api        # generate src/api/generated/schema.ts from ../docs/api/openapi.json
npm run dev                 # Vite dev server (proxies /api to http://127.0.0.1:8000)
npm run lint                # ESLint
npm run typecheck           # tsc --noEmit
npm run test                # Vitest + RTL + MSW
npm run check:api           # fail if generated API types are stale vs the contract
npm run build               # tsc -b && vite build — NEVER on the production VPS
```
Architecture: `docs/FRONTEND_ARCHITECTURE.md`. Security: `docs/FRONTEND_SECURITY.md`.
Auth is memory-only (ADR-017); a browser refresh requires re-login.

### Off-VPS validation via GitHub Actions
Since the production VPS forbids npm (ADR-004), frontend validation runs on a
GitHub-hosted runner. First-time bootstrap produces the lockfile + generated types;
after they are committed, the permanent workflow validates every PR/push with
`npm ci`. Full operator procedure: `docs/FRONTEND_CI_BOOTSTRAP.md`. Workflows:
`.github/workflows/frontend-bootstrap-validation.yml` (manual) and
`.github/workflows/frontend-validation.yml.template` (activate after the lockfile
is committed).

## Migrations (Alembic)
```bash
cd backend
alembic revision --autogenerate -m "describe change"   # create
alembic upgrade head                                    # apply
```
- Never edit an already-applied migration; add a new revision.

## Linting / formatting
- Backend: `ruff` (lint + format) and `mypy` (types).
- Frontend: `eslint` + TypeScript compiler (`tsc --noEmit`).

## Tests
- Backend: `pytest -q` (+ `pytest-asyncio`, `httpx`, in-memory `aiosqlite`).
  134 tests cover auth, RBAC, issue lifecycle, follow-up/void, attachments,
  dashboard (overdue/stagnant/due-this-week), and CSV. Single-process only
  (no `pytest-xdist`); Argon2 makes the suite ~3 min.
- **PostgreSQL integration tests** (`tests/integration/`, 34 tests) are skipped
  unless a test DB URL is set, and run only against a throwaway database:
  `POSTGRES_TEST_DATABASE_URL=postgresql+asyncpg://… pytest -m postgresql`
  (`INTEGRATION_DATABASE_URL` also accepted). They prove concurrent issue-code
  generation (atomic upsert), `FOR UPDATE` lifecycle locking, JSONB/INET,
  DB-level constraints, transaction atomicity, and full migration behavior. The
  isolated-container procedure is in `docs/DEPLOYMENT.md`. Do NOT point them at
  production or the AI-XAUUSD database.

## Commit rules
- Conventional-style messages: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`,
  `test:`.
- One logical change per commit; reference the phase where relevant.
- Never commit `.env`, secrets, dumps, `node_modules`, or build output.
- Do not push to a remote without explicit instruction.

## Repo-local Git identity
This repository was initialized with a **repo-local** neutral identity so commits
are attributable without altering global Git config:
```
git config user.name  "Issue Tracker Dev"
git config user.email "dev@issue-tracker.local"
```
Replace locally with your own identity as needed.
