# Frontend Architecture

> Concept by MrHan (08974747477)
> Phase 2C.1 foundation. Consumes the frozen v1 API (`docs/api/`).

## Stack
React 18 + TypeScript + Vite + Tailwind + React Router 6 (data router) +
TanStack Query 5 + React Hook Form + Zod. Tests: Vitest + React Testing Library +
MSW. Rationale in ADR-018 (fetch + Query) and ADR-019 (generated types).

## Provider composition
```
ErrorBoundary
  └ QueryClientProvider        (server state)
      └ AuthProvider           (session state; clears query cache on logout/401)
          └ RouterProvider     (routes consume auth via context)
```

## Authentication
- **Memory-only token** (ADR-017): the access token lives only in a module closure
  (`src/auth/tokenStore.ts`) — never web storage/cookies. A browser refresh clears
  it, so the app **always starts unauthenticated** and the user logs in again.
- **AuthProvider** exposes `{status, user, login, logout, refreshCurrentUser,
  hasRole}` — the token is **never** exposed via context.
- **Login:** `POST /auth/login` → store token in memory + set user → redirect to the
  intended `/app` route (validated) or the dashboard.
- **Logout:** best-effort `POST /auth/logout` (no server revocation, ADR-009) then
  always clear token + user + `queryClient.clear()` → redirect to login.
- **401:** the API client fires an unauthorized handler → provider tears down the
  session → route guards redirect to `/login`.

## Routing & guards
- `ProtectedRoute` — unauthenticated → `/login` (preserves intended path); loading
  states while checking.
- `RoleRoute allowedRoles=[…]` — insufficient role → `/forbidden` (UX only; backend
  authoritative).
- Routes: `/login`, `/forbidden`, `/app/*` (nested in `AppShell`), global `*` →
  Not Found. `/` and `/app` redirect to `/app/dashboard`.

## API layer
- `client.ts` — native fetch; attaches bearer token; JSON/blob/text/void/multipart;
  `AbortSignal`; normalizes errors to `ApiError`; 401 → unauthorized handler.
- `errors.ts` — `ApiError` (code/status/requestId), safe on non-JSON/HTML bodies.
- `queryClient.ts` — retry ≤1 (never for 4xx auth/validation); no mutation retry;
  `staleTime` 30s; no refetch on focus.
- `types.ts` — readable hand-authored aliases; `generated/schema.ts` — from OpenAPI.

## Application shell
Responsive: fixed desktop sidebar + mobile drawer (Escape closes; overlay click
closes) + top bar (app name, user, role badge, logout). Role-gated navigation from
one config (`components/navigation/navigation.ts`).

## State ownership
- **Server state** → TanStack Query (suggested keys in `docs/api/FRONTEND_HANDOFF.md`).
- **Session state** → AuthProvider context.
- No Redux/MobX/Zustand.

## Validation status & Phase 2C.2 handoff
Placeholders exist for Dashboard, Issues, Meetings, Reports, Users, Audit, Settings.
The scaffold is **not yet runtime-validated**: install/typecheck/test/build run
off-VPS via GitHub Actions (`docs/FRONTEND_CI_BOOTSTRAP.md`). **Phase 2C.2 is
blocked until** the real `package-lock.json` and generated `schema.ts` are committed
and the permanent CI is green. Then 2C.2 implements the Dashboard and Issue
register/detail against the typed client and the documented query keys.
