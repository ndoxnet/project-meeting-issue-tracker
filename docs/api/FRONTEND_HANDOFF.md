# Frontend Integration Handoff

> Concept by MrHan (08974747477)
> Everything the Phase 2C frontend needs to consume the frozen v1 API. The
> backend is authoritative; UI role-gating is cosmetic only.

## API base
```
/api/v1
```
The frontend Nginx container proxies `/api` to the backend (same origin), so the
client uses relative URLs. OpenAPI: `docs/api/openapi.json` (+ `.yaml`).

## Authentication flow (memory-only token — ADR-017)
1. `POST /api/v1/auth/login` `{username, password}` → `{access_token, token_type,
   expires_in, user}`.
2. Store the access token **in memory only** (a module variable / context) —
   **never** `localStorage`/`sessionStorage`/cookies.
3. Attach `Authorization: Bearer <token>` to every request.
4. Call `GET /api/v1/auth/me` to hydrate the current user/role.
5. On **any 401**, clear the in-memory token and redirect to login.
6. A browser refresh loses the token → the user logs in again (acceptable for MVP).
7. Never log the token to the console; never place it in a URL/query string or in
   an error-reporting payload.

`POST /auth/logout` only audits the event and returns success — there is **no**
server-side revocation. The client must discard the token itself.

## Error handling map
| HTTP | Action |
|---|---|
| 401 | clear token → redirect to login |
| 403 | "access denied"; hide the action |
| 404 | not-found view |
| 409 | state conflict → refresh entity, show `error.message` |
| 413 | file too large |
| 415 | unsupported/mismatched file type |
| 422 | form validation — show message near the form |
| 500 | generic error; surface `error.request_id` for support |

All errors share `{ "error": { code, message, request_id } }` (see `ERROR_CODES.md`).

## Role-based UI
Hide actions the current role can't perform (see `AUTHORIZATION.md`), but always
handle 403 — never rely on a hidden button alone.

## Date handling
- Parse timestamp fields (`*_at`) as UTC; display in Asia/Jakarta.
- Do **not** timezone-shift date-only fields (`raised_date`, `due_date`, …).
- Submit date fields as `YYYY-MM-DD`.

## Do NOT use optimistic updates for
issue creation, status transition, close, reopen, archive/restore, or void —
the **server response is the source of truth** (codes are server-assigned; lifecycle
is lock-serialized). Optimistic UI is fine for pure reads/filters.

## Suggested TanStack Query keys
```
["auth", "me"]
["issues", filters]                         // list; filters object drives the key
["issue", issueId]                          // detail
["issue", issueId, "updates"]               // timeline
["issue", issueId, "attachments"]
["dashboard", "summary"]
["dashboard", "overdue"] / ["dashboard","stagnant"] / ...
["master", "categories"] / ["master","responsible-parties"] / ["master","meetings"]
["meeting-occurrences", filters]
["users", filters]
["settings"]
```
Invalidation groups after a mutation:
- create/update/lifecycle issue → invalidate `["issues"]`, `["issue", id]`,
  `["issue", id, "updates"]`, and `["dashboard"]`.
- follow-up/void → `["issue", id, "updates"]`, `["issue", id]`, `["dashboard"]`.
- attachment upload/remove → `["issue", id, "attachments"]`.
- master-data write → the relevant `["master", …]`.

## File download
Use an authenticated `fetch` to `…/attachments/{id}/download`, read the `blob`,
create an object URL, trigger the download, then revoke the URL. Do not embed the
token in the URL.

## CSV export
`GET /api/v1/reports/issues.csv?<same filters as issues list>` returns
`text/csv; charset=utf-8` with `Content-Disposition: attachment; filename="issues.csv"`
and a UTF-8 BOM. Use an authenticated request and a browser download; handle 409
`EXPORT_LIMIT_EXCEEDED` by asking the user to narrow filters.

## Generated types
Do **not** hand-write API types. Generate them off-VPS/CI from the committed spec:
```bash
npx openapi-typescript docs/api/openapi.json \
  --output frontend/src/api/generated/schema.ts
```
> Do not run npm-based type generation on the production VPS.
A domain adapter layer over the generated types is welcome in Phase 2C.
