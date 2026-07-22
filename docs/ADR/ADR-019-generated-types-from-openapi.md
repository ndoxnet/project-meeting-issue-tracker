# ADR-019 — Generated TypeScript Types from OpenAPI

**Status:** Accepted

## Context
The backend v1 OpenAPI contract is frozen (Phase 2B.6) and is the single source
of truth. Hand-writing all API types would drift from the contract.

## Decision
- Generate `frontend/src/api/generated/schema.ts` from `docs/api/openapi.json`
  with **openapi-typescript** (`npm run generate:api`). The file carries a
  "generated — do not edit" header and is committed.
- A drift guard (`npm run check:api`) regenerates and fails on any diff, so the
  committed types can never silently lag the contract.
- A small set of **readable, hand-authored aliases** for the types the app uses
  directly lives in `src/api/types.ts` (sourced from the contract). Broader
  coverage/adapters build on the generated schema in later phases.

### VPS constraint
`openapi-typescript` runs via npm and therefore **only off the production VPS**
(ADR-004). On the VPS the generated file is a committed placeholder; the real
types are generated off-VPS/CI and committed there.

## Consequences
- Types stay aligned with the frozen contract; regeneration is one command.
- Until generated off-VPS, `schema.ts` is a placeholder and `check:api` will show
  it as stale — an intentional, documented reminder.

## Alternatives Considered
- **Hand-written types only:** rejected — drifts from the contract.
- **Runtime schema validation of every response:** deferred — types + contract
  tests are enough for the MVP.
