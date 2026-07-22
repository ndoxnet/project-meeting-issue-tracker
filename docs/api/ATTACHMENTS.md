# Attachment Contract

> Concept by MrHan (08974747477)
> Security details in ADR-014 / `docs/SECURITY.md`. The frontend must always use
> the backend download endpoint — never construct a file path or static URL.

## Upload — `POST /api/v1/issues/{issue_id}/attachments` (`attachments_upload`)
- **Auth:** EDITOR or ADMIN. Request: `multipart/form-data`.
- **Fields:** `file` (binary, required), `description` (string, optional),
  `issue_update_id` (uuid, optional — link the file to a specific timeline entry).
- **Allowed MIME:** `application/pdf`, `image/jpeg`, `image/png` (validated by both
  the declared type **and** leading magic bytes).
- **Max size:** `ATTACHMENT_MAX_MB` (default 10 MB).
- **Errors:** 415 `ATTACHMENT_TYPE_NOT_ALLOWED`, 415 `ATTACHMENT_CONTENT_MISMATCH`,
  413 `ATTACHMENT_TOO_LARGE`, 409 `ISSUE_ARCHIVED`, 404 `ISSUE_NOT_FOUND`.
- **201 response** (`AttachmentResponse`):
```json
{
  "id": "…", "issue_id": "…", "issue_update_id": null,
  "original_filename": "commissioning_punchlist.pdf",
  "stored_filename": "a1b2c3d4e5f6...pdf",
  "mime_type": "application/pdf", "size_bytes": 20481,
  "checksum_sha256": "9f2c…", "description": "Punch list",
  "uploaded_by": "…", "uploaded_at": "2026-07-20T03:00:00Z", "removed_at": null
}
```
`storage_path` is never returned.

## Download — `GET …/attachments/{attachment_id}/download` (`attachments_download`)
- **Auth:** any authenticated role.
- Streams the file with the stored `mime_type` and
  `Content-Disposition: attachment; filename="<original_filename>"` (never inline).
- A **removed** attachment (or missing file) returns 404 `ATTACHMENT_NOT_FOUND`.
- Use an authenticated `fetch` → `blob` → object URL for the browser download; do
  not put the token in the URL.

## List — `GET …/attachments` (`attachments_list`)
Any authenticated role. Returns only non-removed attachments (array of
`AttachmentResponse`), newest first.

## Remove — `POST …/attachments/{attachment_id}/remove` (`attachments_remove`)
- **Auth:** ADMIN only. **Soft remove:** sets `removed_at`/`removed_by`; the
  physical file is retained. After removal the attachment is hidden from the list
  and download returns 404. Idempotent. Audited (`attachment.remove`).
