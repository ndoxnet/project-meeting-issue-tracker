# Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> **Status: Phase 2B — issue lifecycle, follow-up history, attachments,
> dashboard & CSV export.** Backend feature-complete for the MVP and tested
> (134 tests, ruff+mypy clean; 3 PostgreSQL integration tests pending). No
> production stack is running; the frontend is not integrated (Phase 2C).

Internal web app for the Project Control team to record, monitor, and control
issues and follow-ups discussed across many project meetings.

**Core principle:** the **Issue** is the primary entity; a meeting is only a
*source/context* for an update. One issue keeps **one Issue ID** (`ISS-YYYY-NNNN`)
for its whole life, no matter how many meetings discuss it.

## Why
Follow-ups get lost across scattered meeting minutes. This app guarantees every
issue is captured once, with a full chronological history, a PIC, a due date,
next action, status, and clear overdue/stagnant signals — so nothing is forgotten.

## Architecture (overview)
```
Browser → Cloudflare/Host Nginx → 127.0.0.1:5200 (frontend Nginx + SPA)
        → /api → backend (FastAPI :8000, internal) → PostgreSQL (internal)
                                                    → attachments volume
```
- Only the **frontend** binds a host port (`127.0.0.1:5200`).
- **Backend and PostgreSQL are internal-only** (no host ports).
- Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md),
  [docs/DATABASE.md](docs/DATABASE.md), [docs/ADR/](docs/ADR/).

## Repository structure
```
backend/     FastAPI + SQLAlchemy 2 + Alembic (skeleton)
frontend/    React + TS + Vite + Tailwind (skeleton)
deployment/  nginx sample, backup, scripts
docs/        ARCHITECTURE, DATABASE, ADR/, DEPLOYMENT, DEVELOPMENT, SECURITY, USER_FLOWS
storage/     attachment mount point (git-ignored contents)
docker-compose.yml, .env.example, Makefile
```

## Tech stack
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2, asyncpg.
- **Frontend:** React, TypeScript, Vite, Tailwind, React Router, TanStack Query.
- **Database:** PostgreSQL 16 (Alpine), dedicated container, internal-only.
- **Deploy:** Docker Compose; frontend served by Nginx; JWT auth; no Redis (MVP).

## Prerequisites
Docker + Compose v2. For local development off-VPS: Python 3.12 and Node.js LTS.

## Environment setup
```bash
cp .env.example .env     # then fill every CHANGE_ME (never commit .env)
```
Key vars: `SECRET_KEY`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `DISPLAY_TIMEZONE`,
`STAGNANT_DAYS`, `ISSUE_CODE_PREFIX`, `ATTACHMENT_*`, `ADMIN_*`,
`FRONTEND_BIND_HOST/PORT`. See [.env.example](.env.example).

## Local development (plan)
- Backend: `make dev-backend` (dev machine).
- Frontend: `make dev-frontend` (**off-VPS**).
- Validate compose: `make compose-config`.

## ⚠️ Deployment warning
**Do NOT build the frontend on the production VPS.** `npm install` / `vite build`
can spike >1 GB RAM and risk OOM-killing co-located services. Build off-VPS and
push the image; the VPS only pulls it (see
[ADR-004](docs/ADR/ADR-004-build-frontend-outside-vps.md) and
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)).

## Commands
`make help` lists tasks. `compose-build` / `compose-up` are intentionally guarded
against running on the VPS in Phase 1.

## Known limitations (Phase 2B)
- Issue-code concurrency (row locking `FOR UPDATE`) is proven only by the
  PostgreSQL integration tests, which are **pending** (`pytest -m postgresql`);
  SQLite validates logic, not concurrency.
- Migrations validated on SQLite (upgrade/downgrade + `alembic check`); NOT run on
  PostgreSQL / the VPS.
- Access tokens are not revocable server-side; logout = client discards token
  (ADR-009).
- Attachment type check is signature/magic-byte based (no deep parsing / AV).
- Frontend not integrated (Phase 2C). Notifications/email/WhatsApp out of scope.
- No dependency lockfiles committed (installs happen off-VPS).

## Next phase
Phase 2C — frontend implementation (login, shell, dashboard, issue register,
issue form, detail timeline, meetings, master data, users, audit) against the
Phase 2A/2B API.
