# ADR-011 — Transaction-Safe Issue Code Generation

**Status:** Accepted

## Context
Issue codes (`ISS-YYYY-NNNN`) must be unique and gap-tolerant, and must not
collide under concurrent creation. A naive `max(number)+1` is racy.

## Decision
Introduce an `issue_counters` table (`year` PK, `last_number`, `updated_at`).
Within the same transaction that creates the issue, allocate the next number with
an **atomic upsert**:

```sql
INSERT INTO issue_counters (year, last_number) VALUES (:year, 1)
ON CONFLICT (year) DO UPDATE SET last_number = issue_counters.last_number + 1
RETURNING last_number
```

then format `PREFIX-YEAR-NNNN` and insert the issue. `issues.issue_code` UNIQUE is
the final guard; create retries up to 3× as a safety net.

The year is taken from `raised_date` (meaningful and deterministic). The prefix
comes from `ISSUE_CODE_PREFIX`.

> **Phase 2B.5 correction.** The original design used `SELECT … FOR UPDATE` on the
> counter row. PostgreSQL concurrency testing revealed that this locks **nothing**
> when the row does not yet exist (the first issue of a year), so concurrent
> creators all read "no row", all mint `0001`, and collide. The atomic upsert
> fixes this: `INSERT … ON CONFLICT DO UPDATE … RETURNING` serializes concurrent
> increments on the row and returns a distinct number to each transaction, even on
> first creation. No migration change was needed (code-only fix).

## Consequences
- Concurrent creators serialize on the counter row and each receive a unique,
  contiguous number — **proven** by the PostgreSQL integration tests (20 and 50
  concurrent creates → unique codes 1..N, no gaps, no duplicates).
- Portable: the upsert works on PostgreSQL and on SQLite ≥ 3.35 (RETURNING), used
  by the unit tests.
- Gaps are still possible if a create rolls back after allocating (acceptable).

## Alternatives Considered
- **`SELECT … FOR UPDATE`**: rejected — does not lock a not-yet-existing row.
- **DB sequence per year**: less portable, awkward to reset per year.
- **`max()+1`**: rejected — racy.
