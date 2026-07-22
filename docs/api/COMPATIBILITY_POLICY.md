# API Compatibility Policy

> Concept by MrHan (08974747477)
> Current API version: **v1** (`/api/v1`, `info.version` `0.2.0`). Do not introduce
> `/api/v2` now. This policy governs changes to the frozen contract.

## Non-breaking (allowed without a version bump)
- Adding an **optional** response field.
- Adding an **optional** query parameter (with a safe default).
- Adding a new endpoint / operationId.
- Adding a new error `code` for a case previously covered by a generic code
  (announce it; clients must already handle the generic HTTP status).
- Documentation clarifications and added examples.
- Adding an enum value **only** where clients are documented to tolerate unknowns
  (otherwise treat as breaking).

## Breaking (requires the process below)
- Changing an endpoint path or HTTP method.
- Adding a **required** request field; removing/renaming any field.
- Removing an enum value; changing a field's type.
- Changing response shape (e.g. pagination `meta` → something else).
- Changing authorization for an endpoint (tighter or looser) in a way that affects
  clients.
- Changing the semantics of a date/status field (e.g. overdue definition).
- Changing an existing `operationId` (breaks generated clients).

## Process for a breaking change
1. Write an **ADR** describing the change and migration.
2. Add a **CHANGELOG** entry.
3. Consider an API **version** (`/api/v2`) if clients can't migrate in lockstep.
4. Regenerate `docs/api/openapi.json` + `.yaml` (`make openapi-export`).
5. Review **frontend impact**; update the generated types.
6. Update **contract tests** (operation count, security, documented routes) so the
   drift guard passes intentionally, not accidentally.

## Contract drift guard
`tests/contract/test_documented_routes.py::test_committed_openapi_not_stale` fails
if the committed `openapi.json` differs from the live app. The expected operation
count is asserted in `test_openapi_schema.py` and must be updated deliberately when
endpoints change — this is the mechanism that prevents silent contract drift.
