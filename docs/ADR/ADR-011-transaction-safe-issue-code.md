# ADR-011 — Transaction-Safe Issue Code Generation

**Status:** Accepted

## Context
Issue codes (`ISS-YYYY-NNNN`) must be unique and gap-tolerant, and must not
collide under concurrent creation. A naive `max(number)+1` is racy.

## Decision
Introduce an `issue_counters` table (`year` PK, `last_number`, `updated_at`).
Within the same transaction that creates the issue:
1. `SELECT ... FOR UPDATE` the counter row for the issue's **raised-date year**
   (creating it at 0 if absent),
2. increment `last_number`,
3. format `PREFIX-YEAR-NNNN`,
4. insert the issue.
`issues.issue_code` UNIQUE is the final guard; create retries up to 3× on a
uniqueness conflict.

The year is taken from `raised_date` (meaningful and deterministic). The prefix
comes from `ISSUE_CODE_PREFIX`.

## Consequences
- On PostgreSQL the row lock serializes concurrent creators → no duplicate
  numbers. Gaps are possible (acceptable).
- On SQLite (tests) the lock clause is ignored, but the DB-level write lock
  serializes writers; true concurrency is proven by the PostgreSQL integration
  test (pending, `pytest -m postgresql`).

## Alternatives Considered
- **DB sequence per year**: less portable, awkward to reset per year.
- **`max()+1`**: rejected — racy without locking.
