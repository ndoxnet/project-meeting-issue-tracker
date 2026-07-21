# ADR-001 — Issue as the Primary Entity

**Status:** Accepted

## Context
Follow-ups are currently lost because they are scattered across many meeting
minutes. The same issue is discussed in multiple meetings (Weekly Progress,
Construction, Commissioning, …). The team needs one stable identity per issue and
a single place to see its full history.

## Decision
The **Issue** is the primary aggregate. A meeting (via `meeting_occurrences`) is
only a *source/context* for an `issue_update`. Each issue owns exactly one
`issue_code` (e.g. `ISS-2026-0001`) for its entire life, regardless of how many
meetings touch it. History is captured as append-only `issue_updates` linked to
the issue and, optionally, to the meeting occurrence.

## Consequences
- A single chronological timeline per issue is trivial to render.
- Meetings never "own" an issue; they reference it.
- The `issue_code` never changes and never repeats.
- Reporting (overdue, stagnant, closed-this-month) is issue-centric and simple.

## Alternatives Considered
- **Meeting-centric model** (issues nested under meetings): rejected — it
  fragments an issue across meetings and reproduces the current problem.
- **Free-form notes per meeting**: rejected — no stable identity, no control.
