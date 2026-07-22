# ADR-018 — Native fetch + TanStack Query (no Axios, no Redux)

**Status:** Accepted

## Context
The frontend needs an HTTP client and a way to manage server and session state.
The contract is small and same-origin; bundle size and simplicity matter.

## Decision
- **HTTP:** a thin typed wrapper (`src/api/client.ts`) over the browser's native
  `fetch` — no Axios. It attaches the in-memory bearer token, normalizes errors to
  `ApiError`, supports JSON/blob/text/void/multipart, `AbortSignal`, and invokes an
  unauthorized handler on 401. It is framework-agnostic (not tied to React).
- **Server state:** **TanStack Query** (retry ≤1 for transient errors; never for
  401/403/404/409/413/415/422; no mutation auto-retry; cache cleared on logout).
- **Session state:** **React Context** (`AuthProvider`) — not Redux/MobX/Zustand.

## Consequences
- Minimal dependencies; no Axios interceptor stack; smaller bundle.
- Manual response parsing is centralized in one small module and unit-tested.

## Alternatives Considered
- **Axios:** rejected — native fetch is sufficient; avoids a dependency.
- **Redux/MobX/Zustand for auth:** rejected — Context + Query cover the needs
  without a global store framework.
