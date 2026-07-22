# Dashboard Contract

> Concept by MrHan (08974747477)
> All dashboard endpoints require any authenticated role and **exclude archived
> issues**. Derived metrics use the local date (Asia/Jakarta). Definitions are
> canonical in ADR-015.

## Definitions
- **Active** = not archived and status ≠ CLOSED.
- **Overdue** = status ≠ CLOSED, not archived, `due_date` set, `due_date < today`.
  (Due *today* is **not** overdue.)
- **Stagnant** = status ≠ CLOSED, not archived, last activity older than
  `STAGNANT_DAYS` (default 7). Last activity = last follow-up, else `raised_date`.
- **Due this week** = active, not closed, `today ≤ due_date ≤ today + 7` inclusive.
- **Closed this month** = status CLOSED with `closed_date` in the current local month.

## Endpoints & responses

### `GET /api/v1/dashboard/summary` → `dashboard_summary`
```json
{
  "open_count": 12, "in_progress_count": 5, "pending_count": 3,
  "reopened_count": 1, "overdue_count": 4, "stagnant_count": 2,
  "due_this_week_count": 6, "closed_this_month_count": 8, "total_active_count": 21
}
```
Every numeric card maps to a filter the frontend can open (see `FILTERS.md`), e.g.
overdue → `/issues?overdue=true`, stagnant → `/issues?stagnant=true`.

### List endpoints (plain arrays of `IssueListItem`)
`dashboard_overdue`, `dashboard_stagnant`, `dashboard_due_this_week`,
`dashboard_recently_updated`. Query: `limit` (overdue/stagnant/due-week default 50,
max 200; recently-updated default 10, max 50). Each item:
```json
{
  "id": "…", "issue_code": "ISS-2026-0007", "title": "…",
  "category_id": "…", "category_name": "Engineering",
  "responsible_party_id": null, "responsible_party_name": null,
  "priority": "HIGH", "status": "IN_PROGRESS",
  "raised_date": "2026-07-10", "pic_name": "Budi", "pic_user_id": null,
  "due_date": "2026-08-01", "days_open": 12,
  "last_update_at": "2026-07-17T03:00:00Z", "days_since_last_update": 5,
  "next_action": "…", "is_overdue": false, "is_archived": false
}
```

### Groupings (plain arrays of `CountByLabel`)
`dashboard_by_category`, `dashboard_by_responsible_party`:
```json
[ { "label": "Engineering", "count": 9 }, { "label": "Procurement", "count": 4 } ]
```

### Trend
`GET /api/v1/dashboard/opened-vs-closed?months=6` → `dashboard_opened_vs_closed`
(`months` default 6, max 24). Opened bucketed by `raised_date`, closed by
`closed_date`:
```json
[ { "month": "2026-02", "opened": 5, "closed": 3 }, { "month": "2026-03", "opened": 7, "closed": 6 } ]
```
