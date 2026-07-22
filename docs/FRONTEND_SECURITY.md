# Frontend Security

> Concept by MrHan (08974747477)
> Phase 2C.1. The backend is always the authority; the frontend adds UX + hygiene.

## Token handling (ADR-017)
- Access token stored **in memory only** — never `localStorage`, `sessionStorage`,
  IndexedDB, or cookies. An ESLint rule blocks `localStorage`/`sessionStorage`.
- Token is sent only as `Authorization: Bearer <token>`; **never** in a URL/query
  string, never logged, and **never exposed via the auth context**.
- Browser refresh loses the session (re-login). Logout and any 401 clear the token.

## Session teardown
- On logout or 401: clear token, clear current user, and **`queryClient.clear()`**
  so sensitive server data does not outlive the session.

## Error handling
- Backend messages are treated as **plain text** (no `dangerouslySetInnerHTML`).
- Raw HTML bodies (e.g. a proxy 502 page) are never surfaced into error messages.
- The generic `ErrorBoundary` shows a message + request id — never a stack trace.
- Request IDs are shown in an expandable "technical details" area only.

## Open-redirect prevention
- The post-login target is validated (`lib/validateRedirect.ts`): only internal
  paths beginning with `/app` are honored; absolute URLs, `//host`, `javascript:`,
  and backslash tricks fall back to the default route.

## Authorization
- Menu items and routes are role-gated for UX, but **hidden UI is not a security
  control** — the backend enforces authorization on every request.

## Build / environment
- Frontend env contains **no secrets** (no `SECRET_KEY`, no `DATABASE_URL`); the
  token is not a build-time variable.
- No production sourcemaps (Vite `build.sourcemap = false`).
- External links (when added) must use `rel="noopener noreferrer"`.

## Testing the guarantees
`tokenStore.test.ts` asserts no web-storage writes; `client.test.ts` asserts the
token is absent from error objects and that 401 triggers teardown;
`validateRedirect.test.ts` covers open-redirect cases; logout tests assert cache
clearing even when the backend logout call fails.
