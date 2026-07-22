# Filter & Pagination Contract

> Concept by MrHan (08974747477)
> Applies to `GET /api/v1/issues` (`issues_list`). `GET /api/v1/reports/issues.csv`
> (`reports_issues_csv`) accepts the **same filters** except pagination/sort.
> Parameter names below are exactly as implemented.

## Issue-list query parameters
| Param | Type | Default | Multiple | Notes |
|---|---|---|---|---|
| `search` | string | — | no | ILIKE over issue_code, title, description, pic_name, next_action |
| `issue_code` | string | — | no | exact match |
| `status` | enum | — | **yes** (repeat param) | `?status=OPEN&status=PENDING` |
| `priority` | enum | — | no | LOW/MEDIUM/HIGH/CRITICAL |
| `category_id` | uuid | — | no | |
| `responsible_party_id` | uuid | — | no | |
| `pic_user_id` | uuid | — | no | |
| `pic_name` | string | — | no | ILIKE |
| `meeting_id` | uuid | — | no | issues raised in any occurrence of this meeting type |
| `meeting_occurrence_id` | uuid | — | no | |
| `raised_date_from` / `raised_date_to` | date | — | no | inclusive, `YYYY-MM-DD` |
| `due_date_from` / `due_date_to` | date | — | no | inclusive |
| `updated_from` / `updated_to` | datetime | — | no | UTC ISO |
| `overdue` | bool | — | no | status≠CLOSED, not archived, due_date < local today |
| `stagnant` | bool | — | no | last activity older than `STAGNANT_DAYS` |
| `include_archived` | bool | `false` | no | archived excluded by default |
| `sort_by` | enum | — | no | allow-list (below); unknown values are ignored |
| `sort_order` | `asc`\|`desc` | `asc` | no | |
| `page` | int ≥1 | `1` | no | |
| `page_size` | int 1–200 | `20` | no | |

CSV export additionally caps output at **10,000 rows** (`EXPORT_LIMIT_EXCEEDED`)
and does not accept `page`/`page_size`/`sort_*`.

## Sort allow-list
`issue_code`, `raised_date`, `due_date`, `last_update_at`, `updated_at`,
`priority`, `status`. Any other `sort_by` value is silently ignored (no injection).

## Default ordering (when `sort_by` is absent)
1. Priority CRITICAL → HIGH → MEDIUM → LOW,
2. overdue first,
3. nearest `due_date` (nulls last),
4. most recently updated.

## Pagination semantics
- `page` default 1; `page_size` default 20, max 200.
- `meta.total` is the total matching rows; `meta.pages = ceil(total/page_size)`.
- A `page` beyond the last returns an **empty** `items` array with correct `meta`.
- Ordering is stable for a given filter set — safe to sync `page`, `page_size`,
  `sort_by`, `sort_order`, and all filters into the URL query string for shareable,
  reproducible views.
