# ADR-007 — UTC Storage, Local Display (Asia/Jakarta)

**Status:** Accepted

## Context
Users are in Balikpapan and think in local time (WITA, UTC+8 — configured as
`Asia/Jakarta` per spec `DISPLAY_TIMEZONE`). Storing local timestamps invites
ambiguity and bugs (DST-like edge cases, server relocation, comparisons).

## Decision
- Store **all timestamps in UTC** using `timestamptz`.
- Store **date-only business fields** (`raised_date`, `due_date`, `meeting_date`,
  etc.) as `date`.
- Apply the **display timezone** (`Asia/Jakarta`) only at the presentation layer.
- **Overdue / stagnant** comparisons use the **current local date** derived from
  the configured display timezone, so "today" matches the user's calendar.

## Consequences
- Unambiguous storage and correct cross-timezone behavior.
- The app must convert consistently at the edges (API serialization / UI).
- Date-only fields avoid off-by-one-day errors from timezone shifts.

## Alternatives Considered
- **Store local time**: rejected — ambiguous, fragile, hard to compare.
- **Store UTC but compare overdue in UTC**: rejected — could flag an issue overdue
  a few hours early/late relative to the user's actual day.
