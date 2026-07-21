# ADR-010 — Service / Repository Boundaries

**Status:** Accepted

## Context
The codebase needs a clear separation between HTTP concerns, business rules, and
data access — without the ceremony of a generic framework that would be
over-engineering for this MVP.

## Decision
Use a pragmatic three-layer flow:

```
API endpoint  ->  service  ->  repository  ->  async DB session
```

- **Endpoints** (`app/api/v1/endpoints`): parse/validate input (Pydantic),
  enforce role dependencies, call a service, serialize the response. No business
  logic, no direct queries.
- **Services** (`app/services`): business validation, authorization nuances,
  **transaction boundaries** (the service calls `commit`), and **audit creation**
  (staged in the same transaction as the change — atomic, no half-successful ops).
- **Repositories** (`app/repositories`): focused query/persistence helpers and
  pagination. Thin functions, no business rules.

Explicitly avoided: generic repository super-classes, a DI container, command bus,
event sourcing, and a heavyweight unit-of-work framework.

## Consequences
- Easy to test each layer; audit and business changes commit together.
- Some small duplication across entities is accepted over premature abstraction
  (the three identical named routers use one small factory, not a framework).

## Alternatives Considered
- **Fat endpoints with inline SQL**: rejected — mixes concerns, hard to test.
- **Generic CRUD framework**: rejected — over-engineered for this scope.
