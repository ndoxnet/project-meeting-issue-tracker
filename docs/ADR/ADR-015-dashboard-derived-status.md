# ADR-015 — Dashboard & Derived Status Definitions

**Status:** Accepted

## Context
Overdue, stagnant, days-open, and "due this week" must have single, unambiguous
definitions, computed consistently and portably (SQLite tests + PostgreSQL prod).

## Decision
Derived values are **computed, not stored** (except the documented `last_update_*`
denormalization). Definitions (local date via `DISPLAY_TIMEZONE`, ADR-007):

- **days_open** = `local_today - raised_date` (min 0).
- **days_since_last_update** = `local_today - effective_last_activity`, where
  effective is `last_update_at.date()` if a follow-up exists, else `raised_date`.
  The initial "Issue raised" event does **not** set `last_update_at`, so a
  freshly-raised, un-followed-up issue ages from its raised date.
- **overdue** = status ≠ CLOSED **and** not archived **and** `due_date` is set
  **and** `due_date < local_today`. (Due *today* is NOT overdue.)
- **stagnant** = status ≠ CLOSED **and** not archived **and** effective last
  activity older than `STAGNANT_DAYS` (default 7).
- **due this week** = active, not closed, `local_today ≤ due_date ≤ local_today+7`
  (inclusive).
- **closed this month** = status CLOSED with `closed_date` in the current local
  month.
- **opened vs closed trend** = opened bucketed by `raised_date`, closed by
  `closed_date`, per month, over a bounded range (default 6, max 24 months).
  Bucketing is done in Python (no `strftime`/`to_char`) for dialect portability.

All dashboard queries exclude archived issues.

## Consequences
- One source of truth for each metric; no drift between list, detail, and
  dashboard. Slightly more computation per request (acceptable at this scale).

## Alternatives Considered
- **Persisted `is_overdue`/`is_stagnant` flags**: rejected — would need a
  scheduler to recompute daily; violates the "don't store easily-derived" rule.
