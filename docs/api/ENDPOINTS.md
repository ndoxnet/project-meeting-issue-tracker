# API Endpoint Inventory

> Concept by MrHan (08974747477)
> Generated from `docs/api/openapi.json` (frozen **v1**, base path `/api/v1`).
> Auth = Bearer JWT unless marked Public. Roles reflect actual route dependencies;
> the backend is always authoritative (UI role-gating is cosmetic).

## Health

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/ping` | `meta_ping` | Public | 200 |
| GET | `/health` | `health_check` | Public | 200 |

## Authentication

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| POST | `/api/v1/auth/login` | `auth_login` | Public | 200 |
| POST | `/api/v1/auth/logout` | `auth_logout` | Any authenticated | 200 |
| GET | `/api/v1/auth/me` | `auth_get_current_user` | Any authenticated | 200 |

## Users

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/users` | `users_list` | ADMIN | 200 |
| POST | `/api/v1/users` | `users_create` | ADMIN | 201 |
| GET | `/api/v1/users/{user_id}` | `users_get` | ADMIN | 200 |
| PATCH | `/api/v1/users/{user_id}` | `users_update` | ADMIN | 200 |
| POST | `/api/v1/users/{user_id}/activate` | `users_activate` | ADMIN | 200 |
| POST | `/api/v1/users/{user_id}/deactivate` | `users_deactivate` | ADMIN | 200 |
| POST | `/api/v1/users/{user_id}/reset-password` | `users_reset_password` | ADMIN | 200 |

## Categories

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/categories` | `categories_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/categories` | `categories_create` | ADMIN | 201 |
| GET | `/api/v1/categories/{item_id}` | `categories_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/categories/{item_id}` | `categories_update` | ADMIN | 200 |
| POST | `/api/v1/categories/{item_id}/activate` | `categories_activate` | ADMIN | 200 |
| POST | `/api/v1/categories/{item_id}/deactivate` | `categories_deactivate` | ADMIN | 200 |

## Responsible Parties

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/responsible-parties` | `responsible_parties_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/responsible-parties` | `responsible_parties_create` | ADMIN | 201 |
| GET | `/api/v1/responsible-parties/{item_id}` | `responsible_parties_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/responsible-parties/{item_id}` | `responsible_parties_update` | ADMIN | 200 |
| POST | `/api/v1/responsible-parties/{item_id}/activate` | `responsible_parties_activate` | ADMIN | 200 |
| POST | `/api/v1/responsible-parties/{item_id}/deactivate` | `responsible_parties_deactivate` | ADMIN | 200 |

## Meetings

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/meetings` | `meetings_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/meetings` | `meetings_create` | ADMIN | 201 |
| GET | `/api/v1/meetings/{item_id}` | `meetings_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/meetings/{item_id}` | `meetings_update` | ADMIN | 200 |
| POST | `/api/v1/meetings/{item_id}/activate` | `meetings_activate` | ADMIN | 200 |
| POST | `/api/v1/meetings/{item_id}/deactivate` | `meetings_deactivate` | ADMIN | 200 |

## Meeting Occurrences

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/meeting-occurrences` | `meeting_occurrences_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/meeting-occurrences` | `meeting_occurrences_create` | EDITOR, ADMIN | 201 |
| GET | `/api/v1/meeting-occurrences/{occ_id}` | `meeting_occurrences_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/meeting-occurrences/{occ_id}` | `meeting_occurrences_update` | EDITOR, ADMIN | 200 |

## Issues

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/issues` | `issues_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/issues` | `issues_create` | EDITOR, ADMIN | 201 |
| GET | `/api/v1/issues/{issue_id}` | `issues_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/issues/{issue_id}` | `issues_update` | EDITOR, ADMIN | 200 |
| POST | `/api/v1/issues/{issue_id}/archive` | `issues_archive` | ADMIN | 200 |
| POST | `/api/v1/issues/{issue_id}/close` | `issues_close` | EDITOR, ADMIN | 200 |
| POST | `/api/v1/issues/{issue_id}/reopen` | `issues_reopen` | EDITOR, ADMIN | 200 |
| POST | `/api/v1/issues/{issue_id}/restore` | `issues_restore` | ADMIN | 200 |
| POST | `/api/v1/issues/{issue_id}/status` | `issues_change_status` | EDITOR, ADMIN | 200 |

## Issue Updates

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/issues/{issue_id}/updates` | `issue_updates_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/issues/{issue_id}/updates` | `issue_updates_create` | EDITOR, ADMIN | 201 |
| GET | `/api/v1/issues/{issue_id}/updates/{update_id}` | `issue_updates_get` | Any (VIEWER+) | 200 |
| POST | `/api/v1/issues/{issue_id}/updates/{update_id}/void` | `issue_updates_void` | ADMIN | 200 |

## Attachments

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/issues/{issue_id}/attachments` | `attachments_list` | Any (VIEWER+) | 200 |
| POST | `/api/v1/issues/{issue_id}/attachments` | `attachments_upload` | EDITOR, ADMIN | 201 |
| GET | `/api/v1/issues/{issue_id}/attachments/{attachment_id}/download` | `attachments_download` | Any (VIEWER+) | 200 |
| POST | `/api/v1/issues/{issue_id}/attachments/{attachment_id}/remove` | `attachments_remove` | ADMIN | 200 |

## Dashboard

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/dashboard/by-category` | `dashboard_by_category` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/by-responsible-party` | `dashboard_by_responsible_party` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/due-this-week` | `dashboard_due_this_week` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/opened-vs-closed` | `dashboard_opened_vs_closed` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/overdue` | `dashboard_overdue` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/recently-updated` | `dashboard_recently_updated` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/stagnant` | `dashboard_stagnant` | Any (VIEWER+) | 200 |
| GET | `/api/v1/dashboard/summary` | `dashboard_summary` | Any (VIEWER+) | 200 |

## Reports

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/reports/issues.csv` | `reports_issues_csv` | Any (VIEWER+) | 200 |

## Settings

| Method | Path | operationId | Roles | Success |
|---|---|---|---|---|
| GET | `/api/v1/settings` | `settings_list` | Any (VIEWER+) | 200 |
| GET | `/api/v1/settings/{key}` | `settings_get` | Any (VIEWER+) | 200 |
| PATCH | `/api/v1/settings/{key}` | `settings_update` | ADMIN | 200 |

## Notes
- Pagination: `users_list`, `issues_list`, and master-data `*_list` return `Page_*` envelopes (`items` + `meta`). Dashboard list endpoints return plain arrays.
- `reports_issues_csv` returns `text/csv` (not JSON) with a `Content-Disposition` attachment header and a UTF-8 BOM.
- `attachments_upload` uses `multipart/form-data`; `attachments_download` streams the file with `Content-Disposition: attachment`.
- Audit actions and error codes per endpoint are in `ERROR_CODES.md` and the service layer.
