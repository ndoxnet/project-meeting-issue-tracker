# Field Semantics

> Concept by MrHan (08974747477)
> Timestamps are UTC ISO-8601 (`...Z`); date-only fields are `YYYY-MM-DD`.
> Clients display in Asia/Jakarta but must **not** timezone-shift date-only fields.

## Dates vs timestamps
- **Date-only** (`date`): `raised_date`, `due_date`, `closed_date`, `update_date`,
  `target_date`, `meeting_date`, and the `*_from` / `*_to` filters. Send/return
  `YYYY-MM-DD`. Render as-is; never apply a timezone offset.
- **Timestamp** (`timestamptz`, UTC): `last_update_at`, `created_at`, `updated_at`,
  `reopened_at`, `archived_at`, `uploaded_at`, `removed_at`, `voided_at`,
  `last_login_at`. Parse as UTC, display in Asia/Jakarta.

## Issue fields
- `issue_code` — immutable, unique, `ISS-YYYY-NNNN`; server-assigned (never sent
  by clients). Year comes from `raised_date`.
- `raised_date` — when the issue was first raised (business date).
- `due_date` — target date; must be ≥ `raised_date`. May be null.
- `status` — **current** status (`OPEN/IN_PROGRESS/PENDING/CLOSED/REOPENED`).
- `next_action` — current next action; **cleared to null on close** (the last value
  remains visible in the timeline).
- `last_update_summary` / `last_update_at` — denormalized snapshot of the most
  recent **follow-up** (the initial "Issue raised" event does not set these, so a
  freshly-raised issue has `last_update_at = null` and ages from `raised_date`).
- `closed_date` / `closure_note` — the **most recent** closure. On reopen they are
  **retained** as the last closure; a later close overwrites them. All prior
  closures remain in the timeline and audit log.
- `reopened_at` — set when the issue was last reopened (non-null ⇒ has been
  reopened); does not clear `closed_date`/`closure_note`.
- `archived_at` / `archived_by` — soft archive; archived issues are excluded from
  default lists and dashboards and must be restored before edits.

## Timeline (issue update) fields
Each `issue_updates` row is **append-only**. `status` here is the *timeline*
status change, distinct from the issue's current status:
- `status_before` / `status_after` — captured only when the update changed status.
- `due_date_before` / `due_date_after` — captured only when the due date changed.
- `pic_before` / `pic_after` — captured only when the PIC changed.
- `progress_percentage` — 0–100, optional.
- `voided_at` / `voided_by` / `void_reason` — a **voided** update stays in history
  (it is *not* deleted) and does **not** rewind current issue state.

## Attachment fields
- `stored_filename` — server-generated random name (not the user's filename).
- `original_filename` — sanitized user filename (display only).
- `checksum_sha256` — integrity hash.
- `removed_at` / `removed_by` — soft remove. A **removed** attachment is hidden and
  un-downloadable, but the physical file is retained (not deleted) — distinct from
  a physical deletion, which the UI never performs.
- `storage_path` is internal and **never** exposed in responses.
