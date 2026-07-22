# Deployment Plan — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> **Plan only.** Phase 1 does not execute any of this. No build, no `up`, no
> migration is run on the VPS in Phase 1.

## Target environment
- VPS Ubuntu 24.04, 2 cores, ~2–3 GB free RAM, swap full, ~19 GB free disk.
- Docker + Docker Compose v2 present. Host Nginx + Cloudflare Tunnel exist and
  are **not modified** by this project.
- Only the frontend binds a host port: `127.0.0.1:5200`.

## Build & artifact strategy (see ADR-004)
1. **Build the frontend image OUTSIDE the VPS** (developer machine or CI). Prereqs
   in CI before `docker build`: `npm ci`, `npm run generate:api` (+ `npm run
   check:api` drift guard), `npm run lint`, `npm run typecheck`, `npm run test`,
   then `docker build -t <registry>/issue-tracker-frontend:<tag> ./frontend`.
   The Dockerfile uses `npm ci` (committed `package-lock.json`) and produces no
   production sourcemaps.
2. Optionally build the backend image off-VPS too (smaller/safer), or build it on
   the VPS only if resources allow at a quiet time.
3. **Push** images to a registry the VPS can pull from.
4. On the VPS, **pull** the images — never `docker compose build` the frontend on
   the VPS in production.

## First deploy (planned sequence)
1. Copy `.env.example` → `.env` on the VPS; fill all `CHANGE_ME` values
   (strong `SECRET_KEY` via `openssl rand -hex 32`, DB password, admin creds).
2. `docker compose --env-file .env pull` (images only).
3. `docker compose --env-file .env up -d postgres` and wait for healthy.
4. **Run migrations** (Alembic) via the backend image:
   `docker compose run --rm backend alembic upgrade head`.
5. **Create the admin** securely from env (seed script; password never hardcoded).
6. `docker compose up -d backend frontend`.
7. Health checks: backend `/health`, frontend root, Postgres healthcheck.
8. Only after local verification, wire the host Nginx vhost + Cloudflare route to
   `127.0.0.1:5200` (a **separate, approved** step — not part of app deploy).

## Database
- Dedicated Postgres container, **no host port**, named volume
  `issue_tracker_postgres_data`. Never the AI-XAUUSD Postgres.

## Backup (see `deployment/backup/`)
- Nightly `pg_dump` (custom format) to `deployment/backup/` then off-host.
- Periodic copy of the attachments volume.
- Retention documented; backups contain data — store securely, restrict access.

## Migration
- Schema changes only via Alembic revisions in `backend/alembic/versions/`.
- Forward: `alembic upgrade head`. Never edit applied migrations in place.

## Health check
- Backend: `GET /health` → `{"status":"ok", ...}`.
- Compose healthchecks gate `depends_on` ordering.

## Rollback
- App: redeploy the previous image tag (`docker compose up -d` with prior tag).
- Schema: apply a **down** revision only if the migration is reversible and data-
  safe; otherwise restore from the pre-migration `pg_dump`.
- Always take a fresh `pg_dump` immediately before a migration or upgrade.

## Log rotation
- Container stdout/stderr: configure Docker `json-file` log driver with
  `max-size`/`max-file` (documented at deploy time) to bound disk usage.

## Connection pool (production)
The backend async engine uses a conservative pool for the resource-constrained
VPS (`app/db/session.py`, applied only for `postgresql` URLs):
`pool_size=5`, `max_overflow=5`, `pool_timeout=30`, `pool_recycle=1800`,
`pool_pre_ping=True`, `echo=False`. Raise `pool_size`/`max_overflow` only if
sustained concurrency warrants it and RAM allows. `echo` stays False so SQL and
credentials never reach logs.

## PostgreSQL validation (Phase 2B.5) — isolated, throwaway
Validate the backend against real PostgreSQL WITHOUT touching any existing
database or exposing a public port:
1. Resource gate: `uptime; free -h; df -h /` — require ≥1.5 GB RAM free, no swap
   thrashing, ≥10 GB disk.
2. Start an isolated container (unique project/name/network, tmpfs data, loopback
   port only): `docker compose -p issue-tracker-pgtest -f <tmp compose> up -d`.
3. Migrate + verify: `alembic upgrade head`, `alembic check`,
   `alembic downgrade base`, `alembic upgrade head`.
4. `POSTGRES_TEST_DATABASE_URL=… pytest -m postgresql -q`.
5. Cleanup: `docker compose -p issue-tracker-pgtest -f <tmp compose> down -v`,
   remove the temp env/compose files, confirm container count returns to baseline.
Never run this against the production DB or the AI-XAUUSD PostgreSQL.
