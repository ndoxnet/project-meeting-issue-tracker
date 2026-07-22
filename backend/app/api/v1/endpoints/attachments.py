# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin, require_any, require_editor
from app.api.deps.context import RequestContext, get_request_context
from app.db.session import get_db
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.schemas.common import Message
from app.services import attachment as attachment_service

router = APIRouter()


@router.get(
    "/{issue_id}/attachments",
    response_model=list[AttachmentResponse],
    operation_id="attachments_list",
)
async def list_attachments(
    issue_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> list[AttachmentResponse]:
    rows = await attachment_service.list_attachments(session, issue_id=issue_id)
    return [AttachmentResponse.model_validate(r) for r in rows]


@router.post(
    "/{issue_id}/attachments",
    response_model=AttachmentResponse,
    status_code=201,
    operation_id="attachments_upload",
)
async def upload_attachment(
    issue_id: uuid.UUID,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    issue_update_id: uuid.UUID | None = Form(None),
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_editor),
) -> AttachmentResponse:
    content = await file.read()
    att = await attachment_service.upload_attachment(
        session,
        issue_id=issue_id,
        content=content,
        declared_mime=file.content_type,
        original_filename=file.filename or "file",
        description=description,
        issue_update_id=issue_update_id,
        actor=actor,
        ctx=ctx,
    )
    return AttachmentResponse.model_validate(att)


@router.get("/{issue_id}/attachments/{attachment_id}/download", operation_id="attachments_download")
async def download_attachment(
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_any),
) -> FileResponse:
    att, path = await attachment_service.get_for_download(
        session, issue_id=issue_id, attachment_id=attachment_id
    )
    # Force download (never inline) with the sanitized original filename.
    return FileResponse(
        path=str(path),
        media_type=att.mime_type,
        filename=att.original_filename,
        content_disposition_type="attachment",
    )


@router.post(
    "/{issue_id}/attachments/{attachment_id}/remove",
    response_model=Message,
    operation_id="attachments_remove",
)
async def remove_attachment(
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
    actor: User = Depends(require_admin),
) -> Message:
    await attachment_service.remove_attachment(
        session, issue_id=issue_id, attachment_id=attachment_id, actor=actor, ctx=ctx
    )
    return Message(message="Attachment removed.")
