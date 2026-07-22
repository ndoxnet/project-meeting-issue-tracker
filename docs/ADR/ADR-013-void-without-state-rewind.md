# ADR-013 — Void Without State Rewind

**Status:** Accepted

## Context
An erroneous follow-up must be retractable without breaking the append-only
guarantee (ADR-005) and without silently rewriting the issue's current state.

## Decision
Voiding an `issue_update` (Admin only, `void_reason` required) sets `voided_at`,
`voided_by`, `void_reason` and nothing else. The row is retained. Void does **not**
rewind the issue's current status/due/PIC.

If the voided update had changed status, due date, or PIC, the API returns a
warning `CURRENT_STATE_NOT_REVERSED`. Reconciling the current state is done by
appending a **new corrective follow-up**, not by mutating history.

## Consequences
- History stays truthful and append-only; corrections are explicit and attributable.
- The operator must consciously post a correcting update — no hidden auto-rewind
  that could contradict other later updates.

## Alternatives Considered
- **Auto-rewind on void**: rejected — ambiguous when later updates exist; risks
  silently undoing legitimate subsequent changes.
- **Hard delete**: rejected — violates append-only/audit integrity.
