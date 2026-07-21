# Security — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> Phase 1 documents the security model; enforcement is implemented in Phase 2+.

## Secrets
- All secrets via environment variables (`.env`, git-ignored). No secret has a
  production-usable default. `.env.example` uses `CHANGE_ME` placeholders only.
- `SECRET_KEY` generated with `openssl rand -hex 32`.

## Password hashing
- Passwords stored only as a strong hash (bcrypt or argon2 via passlib).
- Plaintext passwords are never stored or logged.

## Authentication & sessions
- Stateless **JWT** bearer tokens; expiry via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- No Redis/session store in the MVP (ADR-003).

## Authorization (RBAC)
- Roles: `ADMIN`, `EDITOR`, `VIEWER`. Enforced **server-side** on every endpoint.
- `VIEWER` is read-only. Void/archive are `ADMIN`-only. Editing a closed issue
  requires reopen (or Admin).

## Input validation
- Pydantic v2 schemas validate all request bodies. Critical validation
  (due ≥ raised, status transitions, progress 0–100) is enforced in the backend,
  never trusting the client.
- SQLAlchemy parameterized queries only — no string-built SQL (SQL-injection safe).

## Secure file upload
- Validate MIME type against `ATTACHMENT_ALLOWED_TYPES` (allow-list).
- Enforce `ATTACHMENT_MAX_MB` size limit (server-side).
- **Sanitize** the original filename; store under a generated `stored_filename`.
- Record `checksum_sha256`. Files live on a dedicated volume, never executed.

## Audit trail
- `audit_logs` records create/edit/status/PIC/due-date/add-update/close/reopen/
  archive and login success/failure, with actor, entity, before/after (redacted),
  IP, and user agent. Audit logs are not editable via the UI.

## Network exposure
- Database has **no host port** and is internal-only. Backend is internal-only.
- Only the frontend binds `127.0.0.1:5200`; public access via host Nginx +
  Cloudflare (outside this project).

## Transport & headers
- Public TLS terminates at Cloudflare/host Nginx.
- Frontend Nginx sets baseline security headers (X-Content-Type-Options,
  X-Frame-Options/frame-ancestors, Referrer-Policy). CORS restricted to
  `ALLOWED_ORIGINS`.

## Rate limiting & login logging
- Login endpoint rate-limited (in-process/DB-backed for the single replica).
- Failed logins logged to `audit_logs` (no password/token values in logs).

## Backup security
- Dumps and attachment copies contain sensitive data — restrict file permissions,
  store off-host securely, and never commit them.

## Log redaction
- Never log passwords, tokens, `SECRET_KEY`, or full attachment contents.
