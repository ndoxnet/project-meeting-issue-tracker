# ADR-006 — Soft Delete and Archive

**Status:** Accepted

## Context
Data may be entered wrongly, and closed/irrelevant issues should be removable from
default views without destroying records. Hard deletion via the UI would break
auditability and risk losing legitimate history.

## Decision
No hard delete through the UI. Instead:
- **Issues** support **archive** (`archived_at`, `archived_by`). Archived issues
  are hidden from default dashboard/register views but remain queryable.
- **Attachments** support soft removal (`removed_at`, `removed_by`).
- **Issue updates** use void (see ADR-005).
Only an **Admin** may archive an issue or void an update.

## Consequences
- Records are always recoverable and auditable.
- Default views stay clean via archive filtering.
- Any true physical deletion (e.g. legal/DB maintenance) is an out-of-band DBA
  action, never a normal UI operation.

## Alternatives Considered
- **Hard delete with confirmation dialog**: rejected — irreversible and breaks
  the audit trail requirement.
