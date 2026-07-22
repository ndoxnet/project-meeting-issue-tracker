# ADR-017 — Memory-Only Access Token for the Frontend MVP

**Status:** Accepted

## Context
The v1 API issues a stateless JWT access token with no server-side revocation
(ADR-009). The Phase 2C frontend must decide where to keep that token. The main
options are `localStorage`, `sessionStorage`, a JS-readable cookie, an HttpOnly
cookie, or in-memory only. Token storage is the frontend's biggest XSS exposure.

## Decision
For the MVP the frontend keeps the access token **in memory only** (a module
variable / auth context) and:
1. Never uses `localStorage`/`sessionStorage`/cookies for the token.
2. Sends it only as `Authorization: Bearer <token>`.
3. Clears the in-memory token on any `401` and redirects to login.
4. Never logs the token or places it in a URL/query string or error-report payload.

A browser refresh loses the token, so the user logs in again — accepted for the MVP.

## Consequences
**Benefits**
- No persistent token for an XSS payload to exfiltrate from storage.
- Simple; matches the stateless, non-revocable token model (ADR-009).

**Limitations**
- Refresh / new tab ⇒ re-login (no silent session resumption).
- No "remember me". A stolen in-memory token is still valid until `exp` (no
  server revocation) — mitigated by a bounded token lifetime.

## Future hardening (not now)
Move to an **HttpOnly, Secure, SameSite** cookie set by the backend (plus CSRF
protection and, optionally, a refresh token) to survive refresh without exposing
the token to JS. That is a backend + frontend change and a separate ADR; this ADR
must not be read as claiming HttpOnly cookies are implemented.

## Alternatives Considered
- **localStorage/sessionStorage:** rejected — readable by any injected script.
- **JS-readable cookie:** rejected — same XSS exposure, adds CSRF surface.
- **HttpOnly cookie now:** deferred — needs CSRF handling and backend changes
  beyond the MVP scope.
