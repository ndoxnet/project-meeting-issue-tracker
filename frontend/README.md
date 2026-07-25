# Frontend — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> React + TypeScript + Vite + Tailwind + React Router + TanStack Query.
> **Phase 2C.1 — auth foundation + application shell.** Domain features (dashboard,
> issues, …) are placeholders pending Phase 2C.2/2C.3.

## ⚠️ Build & test OFF the VPS
`npm install` / `npm run build` / tests must run on a developer machine or CI —
**never on the production VPS** (OOM risk; ADR-004). The lockfile and the generated
API types are produced off-VPS.

> **Runtime validation status:** NOT yet validated. The scaffold has not been
> installed/built/tested at runtime. Use the GitHub Actions bootstrap route
> (`docs/FRONTEND_CI_BOOTSTRAP.md`) or a developer workstation, then commit
> `package-lock.json` + the real `src/api/generated/schema.ts`. **Phase 2C.2 is
> blocked until the permanent CI (`npm ci` + `check:api` + lint + typecheck + test
> + build) is green.**

## Getting started (off-VPS)
```bash
cd frontend
npm install            # creates package-lock.json (commit it)
npm run generate:api   # generate src/api/generated/schema.ts from the OpenAPI spec
npm run check:api      # drift guard
npm run lint && npm run typecheck && npm run test && npm run build
```
Dev server: `npm run dev` (proxies `/api` to `http://127.0.0.1:8000`).
CI route (no dev machine needed): see `docs/FRONTEND_CI_BOOTSTRAP.md`.

## Scripts
- `generate:api` — regenerate types from `../docs/api/openapi.json`.
- `check:api` — regenerate and fail if the committed types are stale (CI drift guard).
- `test` / `test:watch` / `test:coverage` — Vitest + RTL + MSW.

## Implemented (Phase 2C.2 — core tracker)
- **Dashboard** (`/app/dashboard`) — real `/dashboard/summary` KPIs (clickable to
  filtered issues), recently-updated issues, recent meetings.
- **Meetings** (`/app/meetings`, `/app/meetings/:id`) — meeting occurrences +
  their issues (occurrences are the dated instances; types provide the name).
- **Issues** (`/app/issues`) — URL-synced server-side filters (search/status/
  priority/category/overdue) + pagination; detail (`/app/issues/:id`) with the
  follow-up timeline and lifecycle actions (status change / close / reopen /
  add follow-up); create (`/app/issues/new`) and edit (`/app/issues/:id/edit`,
  diff-based PATCH requiring a change reason for PIC/due changes).
- Loading / empty / error / unauthorized (401→login) / not-found states handled.
- All request/response types derive from `src/api/generated/schema.ts`.

## Implemented (Phase 2C.3 — attachments, export, monitoring)
- **Attachments** on the issue detail page — list / upload (Editor/Admin) /
  download / remove (Admin). Client-side size+type pre-check mirrors the backend
  config; backend stays authoritative. 413/415 rejection codes handled distinctly.
- **CSV export** — from the Issue Register (reuses active filters exactly) and the
  **Reports** page; authenticated blob download; `EXPORT_LIMIT_EXCEEDED` handled.
- **Monitoring** — Overdue / Stagnant / Due-this-week views (dedicated dashboard
  endpoints) reachable from the KPI cards; **analytics** distributions + trend as
  dependency-free CSS bars / an accessible table (values always readable as text).
- **Toasts** — accessible live-region notifications supplementing inline errors.

## Implemented (Phase 2C.4A — operational administration)
- **Master data** (`/app/master-data`, ADMIN) — manage categories, responsible
  parties, and meeting types: list with active/inactive filter, create/edit,
  activate/deactivate (contract actions, not delete). Deactivation keeps historical
  values on existing records; inactive items are hidden only from new-record pickers.
- **Meeting-occurrence authoring** (Editor/Admin) — create/edit occurrences from
  the Meetings area (type immutable on edit; diff-based; date-only fields verbatim).
- **Void follow-up updates** (ADMIN) — permanent, reason-required action in the
  issue timeline; the reason survives a recoverable error.

## Implemented (Phase 2C.4B — user administration & read-only settings)
- **Users** (`/app/users`, ADMIN) — list/search/filter, create, edit (email/full
  name/role only), activate/deactivate, role change, reset password. **UX-only**
  self-action guards block self-deactivate/self-role-change (backend enforcement is
  a planned hardening task); the last-admin guard (422) surfaces inline.
- Reset password notes that existing sessions stay valid until backend token
  revocation exists (deactivate to revoke now).
- **Settings** (`/app/settings`, ADMIN) — **read-only** reference view; a banner
  explains runtime config comes from environment configuration, not the DB table.

> **Deferred (production hardening / governance):** editable settings, self-action
> backend enforcement, reset-time session revocation, login rate-limiting.
> **Audit** remains a placeholder — no `GET /audit-logs` in the frozen v1 contract
> (tracked in `docs/backlog/`).

> **Contract mapping:** the API's "meetings" are master *types*; the UI "Meetings"
> are **meeting occurrences** (dated, issue-linked). "Owner" ≈ PIC; issue history =
> the issue-updates timeline. No non-contract fields are invented.

> **Production VPS policy:** Frontend dependency installation, testing,
> typechecking, auditing, and building must not be performed on the production VPS.
> These activities are validated through GitHub Actions (`frontend-validation.yml`).

## Architecture (brief)
- **Auth:** memory-only access token (ADR-017); `AuthProvider` context; a browser
  refresh requires re-login. See `docs/FRONTEND_ARCHITECTURE.md`.
- **API:** native `fetch` client (ADR-018) with normalized `ApiError`; TanStack
  Query for server state.
- **Routing:** `ProtectedRoute` (auth) + `RoleRoute` (role) guards; role-gated
  sidebar; backend is always authoritative.
- **Types:** generated from the frozen OpenAPI contract (ADR-019).

## Layout
```
src/
  api/       client, errors, queryClient, types, generated/schema.ts
  auth/      tokenStore, AuthProvider, guards, useAuth
  app/       AppProviders, router, routes
  components/ layout (AppShell/Sidebar/Topbar), navigation, feedback, ui
  pages/     LoginPage, *PlaceholderPage, Forbidden, NotFound
  config/    env
  hooks/ lib/ styles/ test/
```

## Security notes
Token in memory only (no localStorage/sessionStorage/cookies), never logged, never
in the URL; query cache cleared on logout/401; open-redirect prevented (only `/app`
targets). See `docs/FRONTEND_SECURITY.md`.
