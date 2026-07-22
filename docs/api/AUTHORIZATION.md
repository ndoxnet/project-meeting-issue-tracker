# Authorization Matrix

> Concept by MrHan (08974747477)
> Roles: `VIEWER`, `EDITOR`, `ADMIN`. Enforced **server-side** on every endpoint
> using the user's **current database role** (not the JWT claim alone). The
> frontend may hide actions by role, but the backend is always authoritative.

| Domain | Viewer | Editor | Admin |
|---|---|---|---|
| Authentication self-service (`/auth/me`, `/auth/logout`) | Yes | Yes | Yes |
| User management (`/users` …) | No | No | Full |
| Master-data read (categories / responsible-parties / meetings / settings) | Yes | Yes | Yes |
| Master-data write (create/update/activate/deactivate) | No | No | Full |
| Meeting occurrence read | Yes | Yes | Yes |
| Meeting occurrence create/update | No | Yes | Yes |
| Issue register read (list/detail) | Yes | Yes | Yes |
| Issue create / metadata update | No | Yes | Yes |
| Issue lifecycle (status/close/reopen) | No | Execute | Execute |
| Archive / restore | No | No | Execute |
| Issue update read | Yes | Yes | Yes |
| Issue update create (follow-up) | No | Yes | Yes |
| Void update | No | No | Execute |
| Attachment list / download | Yes | Yes | Yes |
| Attachment upload | No | Yes | Yes |
| Attachment remove | No | No | Yes |
| Dashboard (all) | Yes | Yes | Yes |
| CSV export | Yes | Yes | Yes |
| Settings write | No | No | Yes |

## Dependency mapping
- `require_any` → VIEWER, EDITOR, ADMIN.
- `require_editor` → EDITOR, ADMIN.
- `require_admin` → ADMIN.
- Public (no auth): `health_check`, `meta_ping`, `auth_login` only.

Inactive users cannot act even with a still-valid token (`get_current_active_user`
rejects them → 401 `AUTHENTICATION_FAILED`). Insufficient role → 403
`AUTHORIZATION_FAILED`. Both are enforced in `app/api/deps/auth.py` and verified by
`tests/contract/test_security_contract.py`.
