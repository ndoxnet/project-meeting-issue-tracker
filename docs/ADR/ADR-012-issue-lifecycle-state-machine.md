# ADR-012 — Issue Lifecycle State Machine

**Status:** Accepted

## Context
Status changes must be predictable, validated, and fully historied. Close and
reopen carry extra data (closure note / reason) and need dedicated handling.

## Decision
A central state machine (`app/core/lifecycle.py`) defines allowed transitions:

```
OPEN        -> IN_PROGRESS | PENDING | CLOSED
IN_PROGRESS -> PENDING | CLOSED | OPEN
PENDING     -> IN_PROGRESS | OPEN | CLOSED
CLOSED      -> REOPENED            (reopen endpoint only)
REOPENED    -> IN_PROGRESS | PENDING | CLOSED
```

- The generic `/status` endpoint refuses `-> CLOSED` (use `/close`) and any
  transition out of `CLOSED` (use `/reopen`).
- Every transition (status/close/reopen) writes an append-only `issue_update`
  capturing `status_before`/`status_after`, updates current state, refreshes
  `last_update_at`, writes an audit row — all in one transaction.
- Closed/archived issues reject generic metadata edits and follow-ups.

### Close / reopen data semantics
- **Close:** requires `closure_note` + `closed_date` (≥ raised_date); sets status
  CLOSED; keeps the last `next_action` in history but clears the current one.
- **Reopen:** only from CLOSED; sets status REOPENED and `reopened_at`; **retains**
  the previous `closed_date`/`closure_note` as the last closure. A later close
  overwrites them with the newest closure; all prior closures remain visible in
  the update history and audit log.

## Consequences
- Illegal transitions are impossible via the API; history is complete.

## Alternatives Considered
- **Free-form status set**: rejected — no integrity, ambiguous history.
