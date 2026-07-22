# Frontend — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> React + TypeScript + Vite + Tailwind + React Router + TanStack Query.
> **Phase 2C.1 — auth foundation + application shell.** Domain features (dashboard,
> issues, …) are placeholders pending Phase 2C.2/2C.3.

## ⚠️ Build & test OFF the VPS
`npm install` / `npm run build` / tests must run on a developer machine or CI —
**never on the production VPS** (OOM risk; ADR-004). The lockfile and the generated
API types are produced off-VPS.

## Getting started (off-VPS)
```bash
cd frontend
npm install            # creates package-lock.json (commit it)
npm run generate:api   # generate src/api/generated/schema.ts from the OpenAPI spec
npm run lint
npm run typecheck
npm run test
npm run build
```
Dev server: `npm run dev` (proxies `/api` to `http://127.0.0.1:8000`).

## Scripts
- `generate:api` — regenerate types from `../docs/api/openapi.json`.
- `check:api` — regenerate and fail if the committed types are stale (CI drift guard).
- `test` / `test:watch` / `test:coverage` — Vitest + RTL + MSW.

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
