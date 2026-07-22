# Response Conventions

> Concept by MrHan (08974747477)
> Shapes below match the **actual** implementation (see `openapi.json`). Do not
> assume shapes that differ from this document.

## Resource response
A single resource is returned as a flat JSON object with its fields, e.g. a user:
```json
{
  "id": "3f1c9d2e-0000-4000-8000-000000000010",
  "full_name": "Example Editor",
  "email": "editor@example.invalid",
  "username": "editor1",
  "role": "EDITOR",
  "is_active": true,
  "last_login_at": null,
  "created_at": "2026-07-20T02:15:00Z",
  "updated_at": "2026-07-20T02:15:00Z"
}
```

## Paginated response
Pagination uses an `items` array and a `meta` object (component `PageMeta`).
**Note the exact key names — it is `meta`, not `pagination`.**
```json
{
  "items": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 0,
    "pages": 0
  }
}
```
Applies to: `users_list`, `issues_list`, `categories_list`,
`responsible_parties_list`, `meetings_list`, `meeting_occurrences_list`.
Dashboard list endpoints return **plain arrays** (not paginated).

## Warning response (issue create)
Creating an issue returns the created issue plus optional warnings:
```json
{
  "issue": { "id": "…", "issue_code": "ISS-2026-0002", "...": "..." },
  "warnings": [
    {
      "code": "POSSIBLE_DUPLICATE",
      "issue_id": "3f1c9d2e-0000-4000-8000-000000000001",
      "issue_code": "ISS-2026-0001",
      "title": "Vendor commissioning attendance is pending"
    }
  ]
}
```
Voiding an update returns `{ "update": {...}, "warnings": ["CURRENT_STATE_NOT_REVERSED"] }`.

## Error response
All errors use one envelope (`ErrorResponse` → `ErrorBody`):
```json
{
  "error": {
    "code": "ISSUE_NOT_FOUND",
    "message": "Issue not found",
    "request_id": "9f2c1a7b3d4e5f60"
  }
}
```
- `code` is a stable machine code (see `ERROR_CODES.md`).
- `message` is human-readable and safe to log; some may be shown to users.
- `request_id` echoes the `X-Request-ID` request header (or a generated one) and
  is also returned as the `X-Request-ID` response header.

### Request-body validation (422)
Pydantic request validation returns the same envelope with
`code = "VALIDATION_ERROR"`. The current handler returns a generic message;
field-level detail is intentionally not exposed in the envelope. Clients should
validate forms client-side and treat 422 as "check the form".

## Content types
- JSON for all resource endpoints.
- `text/csv; charset=utf-8` for `reports_issues_csv` (with `Content-Disposition`).
- `multipart/form-data` request for `attachments_upload`; binary stream for
  `attachments_download`.
