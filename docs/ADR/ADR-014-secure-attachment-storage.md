# ADR-014 — Secure Attachment Storage

**Status:** Accepted

## Context
Uploads are an attack surface (type spoofing, path traversal, oversized files,
executable content). The MVP must be safe without heavy OS dependencies.

## Decision
- **Type:** allow-list `application/pdf`, `image/jpeg`, `image/png`. Validate the
  declared MIME **and** verify leading magic bytes (`%PDF-`, `\xFF\xD8\xFF`,
  `\x89PNG…`). Mismatch → `ATTACHMENT_CONTENT_MISMATCH` (415). No `python-magic`
  (avoids a system libmagic dependency) — documented limitation: sniffing is
  signature-based, not full content parsing.
- **Size:** enforce `ATTACHMENT_MAX_MB` server-side → 413.
- **Filename:** the user filename is sanitized to a safe basename (metadata only);
  the stored filename is a random `uuid4.ext`. The storage path is derived solely
  from the issue UUID (`STORAGE_PATH/issues/<issue_uuid>/<random>`), never from
  user input → no path traversal.
- **Integrity:** SHA-256 stored.
- **Atomicity:** file is written, then metadata is committed; if the DB commit
  fails, the orphaned file is deleted (file and DB stay consistent).
- **Serving:** no static directory exposure. Download goes through an
  authenticated endpoint with `Content-Disposition: attachment` (never inline).
- **Removal:** soft (`removed_at`/`removed_by`); no hard delete via UI; removed
  files are hidden and un-downloadable.
- **Authorization:** list/download = any role; upload = Editor+; remove = Admin.

## Consequences
- Strong baseline security with zero system packages.
- Signature sniffing can be fooled by a valid-header-but-malformed file; deep
  validation/AV scanning is a future enhancement.

## Alternatives Considered
- **Object storage (S3/R2)**: deferred — a volume suffices for the MVP.
- **python-magic**: rejected for now — system dependency weight.
