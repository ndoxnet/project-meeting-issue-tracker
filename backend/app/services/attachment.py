# Concept by MrHan (08974747477)
"""Attachment service (ADR-014): secure upload, authorized download metadata,
soft remove. Files are stored under STORAGE_PATH/issues/<issue_uuid>/ with a
random stored filename; the user filename is only sanitized metadata."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.config import get_settings
from app.core.errors import (
    DomainError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
)
from app.models.attachment import Attachment
from app.models.user import User
from app.services import issue as issue_service
from app.services.audit import record_audit
from app.utils.files import (
    generate_stored_filename,
    issue_storage_dir,
    sanitize_filename,
    sha256_of,
    signature_matches,
)


async def list_attachments(
    session: AsyncSession, *, issue_id: uuid.UUID, include_removed: bool = False
) -> list[Attachment]:
    await issue_service.get_issue_or_404(session, issue_id)
    stmt = select(Attachment).where(Attachment.issue_id == issue_id)
    if not include_removed:
        stmt = stmt.where(Attachment.removed_at.is_(None))
    stmt = stmt.order_by(Attachment.uploaded_at.desc())
    return list((await session.execute(stmt)).scalars().all())


async def get_for_download(
    session: AsyncSession, *, issue_id: uuid.UUID, attachment_id: uuid.UUID
) -> tuple[Attachment, Path]:
    att = await session.get(Attachment, attachment_id)
    if att is None or att.issue_id != issue_id or att.removed_at is not None:
        raise DomainError("ATTACHMENT_NOT_FOUND", "Attachment not found", http_status=404)
    path = Path(att.storage_path)
    if not path.is_file():
        raise DomainError("ATTACHMENT_NOT_FOUND", "Attachment file missing", http_status=404)
    return att, path


async def upload_attachment(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    content: bytes,
    declared_mime: str | None,
    original_filename: str,
    description: str | None,
    issue_update_id: uuid.UUID | None,
    actor: User,
    ctx: RequestContext,
    storage_root: str | None = None,
) -> Attachment:
    settings = get_settings()
    issue = await issue_service.get_issue_or_404(session, issue_id)
    if issue.archived_at is not None:
        raise DomainError(
            "ISSUE_ARCHIVED", "Archived issue cannot receive attachments", http_status=409
        )

    max_bytes = settings.ATTACHMENT_MAX_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise PayloadTooLargeError()

    declared = (declared_mime or "").split(";")[0].strip().lower()
    if declared not in settings.attachment_allowed_types_list:
        raise UnsupportedMediaTypeError()
    if not signature_matches(declared, content[:16]):
        # Content does not match its declared type (or extension) — reject.
        raise DomainError(
            "ATTACHMENT_CONTENT_MISMATCH",
            "File content does not match its declared type",
            http_status=415,
        )

    root = storage_root or settings.STORAGE_PATH
    stored_name = generate_stored_filename(declared)
    target_dir = issue_storage_dir(root, issue_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / stored_name
    path.write_bytes(content)

    try:
        att = Attachment(
            issue_id=issue_id,
            issue_update_id=issue_update_id,
            original_filename=sanitize_filename(original_filename),
            stored_filename=stored_name,
            storage_path=str(path),
            mime_type=declared,
            size_bytes=len(content),
            checksum_sha256=sha256_of(content),
            description=description,
            uploaded_by=actor.id,
            uploaded_at=datetime.now(UTC),
        )
        session.add(att)
        await session.flush()
        record_audit(
            session,
            action="attachment.upload",
            entity_type="attachment",
            entity_id=att.id,
            actor_user_id=actor.id,
            after={
                "attachment_id": str(att.id),
                "issue_id": str(issue_id),
                "mime_type": declared,
                "size_bytes": att.size_bytes,
                "checksum_sha256": att.checksum_sha256,
            },
            ctx=ctx,
        )
        await session.commit()
        await session.refresh(att)
        return att
    except Exception:
        # DB failure: remove the orphaned file so file and DB stay consistent.
        path.unlink(missing_ok=True)
        await session.rollback()
        raise


async def remove_attachment(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    actor: User,
    ctx: RequestContext,
) -> Attachment:
    att = await session.get(Attachment, attachment_id)
    if att is None or att.issue_id != issue_id:
        raise DomainError("ATTACHMENT_NOT_FOUND", "Attachment not found", http_status=404)
    if att.removed_at is not None:
        return att  # idempotent soft-remove
    att.removed_at = datetime.now(UTC)
    att.removed_by = actor.id
    record_audit(
        session,
        action="attachment.remove",
        entity_type="attachment",
        entity_id=att.id,
        actor_user_id=actor.id,
        after={"attachment_id": str(att.id), "issue_id": str(issue_id)},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(att)
    return att
