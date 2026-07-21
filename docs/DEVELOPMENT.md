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
pip install -e .            # installs from pyproject.toml (dev machine only)
uvicorn app.main:app --reload --port 8000   # local dev only
```
- Lint: `ruff check app` — Types: `mypy app` — Tests: `pytest`.

## Frontend (local, OFF-VPS)
```bash
cd frontend
npm install                 # off-VPS only (ADR-004)
npm run dev                 # Vite dev server
npm run build               # production build — NEVER on the production VPS
```

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
- Backend: `pytest` (+ `pytest-asyncio`, `httpx` for API tests).
- Phase 2 adds real coverage: auth, RBAC, issue lifecycle, overdue/stagnant, CSV.

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
