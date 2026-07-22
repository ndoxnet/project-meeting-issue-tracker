# ADR-016 — Pessimistic Row Locking for State Transitions

**Status:** Accepted

## Context
Phase 2B used `session.get(Issue, id)` (no lock) before mutating an issue. Under
PostgreSQL READ COMMITTED, two concurrent transitions on the same issue (e.g. two
`close` calls, or two follow-ups changing status) could each read the pre-change
state and both proceed — a lost update / double-close race. Phase 2B.5
concurrency testing on real PostgreSQL confirmed the risk.

## Decision
State-changing issue operations acquire a **row lock** on the target issue with
`SELECT … FOR UPDATE` at the start of the transaction, via
`repositories.issue.get_issue(..., for_update=True)` (exposed as
`services.issue.get_issue_or_404(..., for_update=True)`).

Locked operations: metadata update, status change, close, reopen, archive,
restore, and follow-up create. Read paths (detail, list, dashboard, download,
attachment upload) do **not** lock.

The second concurrent transaction blocks until the first commits, then re-reads
the now-current state and re-validates — so a double-close yields exactly one
success and one `ISSUE_ALREADY_CLOSED`, and an illegal post-change transition is
rejected.

Portability: on SQLite (unit tests) the `FOR UPDATE` clause is ignored, but
SQLite's database-level write lock already serializes writers, so behavior is
consistent; the concurrency guarantee is *proven* on PostgreSQL (`pytest -m
postgresql`).

## Consequences
- Correct, serialized lifecycle transitions with no lost updates.
- Brief lock contention only between concurrent writers of the *same* issue;
  different issues and all readers are unaffected.
- A held lock is released on commit or rollback; the fault-injection tests confirm
  rollback releases it (no stuck locks).

## Alternatives Considered
- **Optimistic concurrency (version column + retry)**: viable but more churn and
  retries; pessimistic locking is simpler for low-contention human workflows.
- **SERIALIZABLE isolation**: heavier; would force broad retry handling for a
  narrow need.
