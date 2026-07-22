# User Flows — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> Reference flows for the MVP. UI is implemented in Phase 3.

## 1. Login
1. User enters username/email + password.
2. Backend verifies the hash, returns a JWT; login recorded in `audit_logs`.
3. On failure, a generic error is shown and the failure is logged.

## 2. Create issue (Editor/Admin)
1. Open **Issues → New**.
2. Fill title (required), description, category, priority, raised date (required),
   raised-in meeting occurrence, responsible party, PIC, due date, next action,
   optional attachment.
3. On submit, a **duplicate check** runs (ILIKE on title/keywords among active
   issues). If similar issues exist, a "Possible duplicate issue found" warning is
   shown; the user may confirm and proceed.
4. Backend generates `issue_code` (`ISS-YYYY-NNNN`), status `OPEN`, writes the
   first `issue_updates` row + audit entry, and opens the detail page.

## 3. Update issue from a meeting (Editor/Admin)
1. From the issue detail, **Add Follow-Up**; or from a meeting occurrence, add
   updates to several issues at once.
2. Fill update date, meeting occurrence (optional), update note, decision, next
   action, action owner, target date, optional new status/due date/PIC, optional
   progress %, optional attachment.
3. Backend appends an `issue_updates` row (capturing before/after for any changed
   status/due date/PIC), refreshes the issue's `last_update_*`, writes audit.

## 4. View timeline
1. Issue detail shows a summary block + a **chronological** timeline of all
   updates (date, meeting, note, decision, next action, owner, target date, status
   change, due-date change, author, timestamp, attachments). Voided rows are shown
   as void.

## 5. Change due date
1. Via Add Follow-Up (or an edit action), set a new due date.
2. Old and new due dates are recorded on the update row and in audit; the issue's
   `due_date` is updated. Overdue is recomputed automatically.

## 6. Close issue (Editor/Admin)
1. **Close** → confirmation dialog requires `closure_note` and `closed_date`.
2. Status → `CLOSED`; append update + audit. The issue is no longer overdue.

## 7. Reopen issue (Editor/Admin)
1. **Reopen** → confirmation dialog requires a reopen reason.
2. Status → `REOPENED`; the previous `closed_date` stays in history; append update
   + audit. The issue returns to active views.

## 8. Filter overdue
1. **Overdue** menu (or a dashboard card) lists issues where status ≠ CLOSED and
   due date < today (local). Filters combine and are reflected in the URL.

## 9. Review stagnant issues
1. A dashboard card / filter lists issues with no update beyond the stagnant
   threshold (default 7 days; configurable). If never updated, `raised_date` is
   the baseline. A clear warning is shown.

## Derived status definitions (canonical — see ADR-015)
All dates use the local display timezone (`Asia/Jakarta`). Archived issues are
excluded from all dashboard views.
- **Overdue:** status ≠ CLOSED, not archived, `due_date` set, `due_date < today`.
  (Due *today* is not overdue.)
- **Stagnant:** status ≠ CLOSED, not archived, last activity older than
  `STAGNANT_DAYS`. Last activity = last follow-up if any, else `raised_date`
  (the initial "Issue raised" event does not count as a follow-up).
- **Due this week:** active, not closed, `today ≤ due_date ≤ today + 7` inclusive.
- **Closed this month:** CLOSED with `closed_date` in the current local month.
- **Void semantics:** a voided update stays in history and never rewinds current
  state; if it had changed status/due/PIC, the API warns
  `CURRENT_STATE_NOT_REVERSED` and a corrective follow-up must be posted.
