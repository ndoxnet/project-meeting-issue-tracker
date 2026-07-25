# Backlog / Mini-Proposal — Read-only `GET /audit-logs` contract addition

> Concept by MrHan (08974747477)
> Status: **PROPOSAL — not implemented.** Raised during Phase 2C.3 because the
> frozen v1 API exposes no way to read the audit trail, so the frontend **Audit**
> screen cannot be built without this backend change. Do not implement until it is
> approved as its own phase.

## Why
The `audit_logs` table is written on every state change (`record_audit`) but has
**no read endpoint** in the frozen v1 contract. The frontend Audit page is
therefore a placeholder. This proposal defines the minimum read-only contract to
unblock it — as a deliberate, reviewed API change, not a side effect of a frontend phase.

## 1. Authorization
- **ADMIN only** (`require_admin`). Audit data is sensitive (actor, IP, user-agent,
  before/after payloads).
- Reads are themselves auditable is out of scope (avoid read-amplification loops).
- No create/update/delete — the table stays append-only (already enforced: no
  mutation endpoints exist).

## 2. Pagination
- Page/size envelope consistent with the rest of the API (`PageMeta`:
  `page`, `page_size`, `total`, `pages`). Default `page_size` 50, hard max 200.
- Default sort `created_at DESC` (indexed). Allow `sort_order` asc/desc on
  `created_at` only.

## 3. Filtering (all optional, indexed columns first)
- `actor_user_id` (uuid), `action` (string, e.g. `issue.close`),
  `entity_type` (string, e.g. `issue`), `entity_id` (uuid),
  `created_from` / `created_to` (date-time range), `request_id` (string).
- Reject unknown/oversized filters via the existing validation error shape.

## 4. Response fields (`AuditLogResponse`)
From `app/models/audit_log.py`, exposed read-only:
`id`, `actor_user_id`, `action`, `entity_type`, `entity_id`, `before_data`,
`after_data`, `request_id`, `ip_address`, `user_agent`, `created_at`.
- **Decision needed:** whether `before_data`/`after_data` (arbitrary JSON that may
  hold PII) are returned in the list, redacted, or only in a per-record
  `GET /audit-logs/{id}` detail. Recommend: summary list **without** payloads +
  a detail endpoint that includes them (both ADMIN-only).
- `ip_address`/`user_agent` are operationally useful but sensitive — confirm they
  belong in the response or should be ADMIN-detail-only.

## 5. Retention implications
- No retention/rotation policy exists today; the table grows unbounded. Before
  exposing reads at scale, decide on: retention window, archival/export, and index
  strategy for range queries (`created_at`, `entity_type`+`entity_id`).
- A read API makes volume visible to users — size the default `page_size` and add
  a `total` cap or keyset pagination if the table is large.

## 6. OpenAPI regeneration
- Add the route(s) with explicit `operation_id`s (`audit_logs_list`, optionally
  `audit_logs_get`), regenerate `docs/api/openapi.json`, then regenerate the
  frontend types (`npm run generate:api`) off-VPS. This is a **contract change** →
  bump/track it deliberately; the freeze note in `docs/api/` must be updated.

## 7. Tests
- Backend: ADMIN-only access (403 for Editor/Viewer/anon); pagination bounds;
  each filter narrows results; payload redaction decision honored; sort order;
  append-only (no write routes). Include an isolated-Postgres integration test for
  range filtering + index use.
- Frontend (future phase): Audit page — list/empty/error, filter→API, ADMIN route
  guard, and (if adopted) payload detail view.

## Out of scope here
Implementation, migrations, and the frontend Audit screen. This document only
scopes the contract so it can be approved and sequenced on its own.
