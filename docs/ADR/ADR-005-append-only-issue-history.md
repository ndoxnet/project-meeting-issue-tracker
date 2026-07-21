# ADR-005 — Append-Only Issue History

**Status:** Accepted

## Context
The team must trust the timeline of an issue. If updates could be edited or
deleted, the audit trail and the "what happened when" story would be unreliable.

## Decision
`issue_updates` is **append-only**. Rows are never hard-deleted or overwritten.
Corrections are made by **voiding** the erroneous row (`voided_at`, `voided_by`,
`void_reason`) and appending a replacement update. Voiding is an **Admin-only**
action. The original row remains stored and visible (marked void) in history.

## Consequences
- The timeline is a faithful, immutable record.
- "Correction" is explicit and attributable, not a silent edit.
- Slightly more rows over time; acceptable for the data volume.

## Alternatives Considered
- **Mutable updates with an edit log**: rejected — more complex and easier to
  misuse than a clear void+replace model.
- **Hard delete for mistakes**: rejected — destroys audit integrity.
