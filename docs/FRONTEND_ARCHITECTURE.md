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

## Core tracker (Phase 2C.2)
- **API layer:** typed fetchers + React Query hooks per domain — `api/issues.ts`,
  `api/meetings.ts`, `api/dashboard.ts`, `api/masterdata.ts` — over the shared
  `api/client.ts`. Types derive from `api/generated/schema.ts` via `api/types.ts`
  (ADR-019). Stable keys in `api/queryKeys.ts`; mutations invalidate `['issues']`,
  `['issue', id]`, `['issue', id, 'updates']`, and `['dashboard']`.
- **Pages** (`pages/tracker/`): TrackerLanding, MeetingsList, MeetingDetail,
  IssuesList, IssueDetail (+ timeline + `features/issues/IssueActions`),
  IssueCreate, IssueEdit. Reusable UI: StatusBadge, PriorityBadge, StatCard,
  Pagination, Field/Select/TextInput/TextArea, Modal, PageHeader, DataState.
- **Contract mapping:** "Meetings" = meeting **occurrences** (dated, issue-linked);
  owner ≈ PIC; history = issue-updates timeline. Lifecycle gating mirrors ADR-012
  in `features/issues/lifecycle.ts` (backend remains authoritative).
- **Dates:** `lib/dates.ts` — date-only fields shown verbatim (no tz shift);
  timestamps shown in Asia/Jakarta.

## Validation
Install/typecheck/lint/test/build run **off-VPS via GitHub Actions**
(`frontend-validation.yml`) — never on the production VPS (ADR-004). The permanent
`npm ci` workflow is the acceptance gate for this phase.

## Attachments, export & monitoring (Phase 2C.3)
- **Attachments** (`features/attachments/`) on the issue detail page: list (all
  roles) / upload (Editor/Admin, non-archived) / download (all roles) / remove
  (Admin). Client-side size+type is a usability pre-check mirroring the backend
  config (`config.ts`); the backend re-validates and is authoritative. Rejection
  codes 413/415 (`ATTACHMENT_TOO_LARGE`, `ATTACHMENT_TYPE_NOT_ALLOWED`,
  `ATTACHMENT_CONTENT_MISMATCH`) are handled distinctly.
- **Downloads** are authenticated blob responses via `apiClient.download`;
  `lib/download.ts` parses+sanitizes the `Content-Disposition` filename (with a
  deterministic fallback) and always revokes the object URL. Blobs/object URLs
  are never cached (download is a mutation, not a query).
- **CSV export** (`features/reports/`, `api/reports.ts`) reuses the register's
  active filters exactly; no pagination/sort is sent (none is contract-exposed).
- **Monitoring** (`pages/tracker/MonitoringPage`) uses the dedicated
  `dashboard_{overdue,stagnant,due_this_week}` endpoints — the logic stays
  server-side. **Analytics** (`features/dashboard/`) render distributions/trend
  with dependency-free CSS bars + an accessible table; values are always text.
- **Toasts** (`components/feedback/ToastProvider`) are accessible live regions
  that supplement — never replace — inline errors.

## Not implemented (deferred)
Users/Audit/Settings remain placeholders; **Audit** is contract-blocked (no
`GET /audit-logs` in the frozen v1 API — a future read-only audit contract is
tracked separately). Void-update UI and admin/master-data management are Phase 2C.4.
