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
- `app/core/redaction.py` recursively redacts sensitive keys (password,
  password_hash, token, access_token, authorization, secret) from audit
  before/after payloads and any structured context.

## Phase 2A implementation status
- **Password hashing:** Argon2id via pwdlib (ADR-008). Policy: 12–128 chars, not
  equal to username/email. Timing equalized for unknown users via a dummy verify.
  Breached-password lookup is NOT implemented in the MVP.
- **Tokens:** PyJWT HS256 (ADR-009). Explicit algorithm allow-list on decode;
  required claims sub/iat/exp/jti; generic 401 on any failure.
- **Token revocation — KNOWN LIMITATION:** access tokens are **not** revocable
  server-side. Logout only audits the event and instructs the client to discard
  the token; the token stays valid until `exp`. No refresh token yet.
- **RBAC:** enforced server-side on every endpoint; authorization uses the
  current **database** role, never the JWT claim alone. Inactive users cannot act
  even with a valid token.
- **Request correlation:** `X-Request-ID` middleware (bounded/validated input),
  echoed on responses and stored in audit rows.
- **Admin bootstrap:** `scripts/bootstrap_admin.py` reads env, is idempotent,
  refuses `CHANGE_ME`, never prints the password.

## Phase 2B additions
- **Attachments (ADR-014):** MIME allow-list + magic-byte signature check
  (mismatch → 415 `ATTACHMENT_CONTENT_MISMATCH`); size cap (413); user filename
  sanitized to a basename, stored under a random `uuid4.ext`; storage path
  derived only from the issue UUID (no path traversal); SHA-256 recorded; file
  deleted if the DB commit fails; download only via an authenticated endpoint
  with `Content-Disposition: attachment` (never inline); soft remove only.
  Limitation: signature sniff is not deep content validation / antivirus.
- **CSV export:** formula-injection mitigation (cells starting with `= + - @` /
  tab / CR are prefixed with `'`); 10,000-row cap (`EXPORT_LIMIT_EXCEEDED`);
  never exports password/hash/token/audit JSON/storage paths; the export action
  is audited with filters + row count only (not the CSV body).
- **Sort safety:** issue-list sorting uses a fixed column allow-list; arbitrary
  request-supplied column names are ignored (no SQL injection via `sort_by`).
- **Void (ADR-013):** Admin-only; never rewinds current state silently.
