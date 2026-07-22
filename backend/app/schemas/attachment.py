# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    issue_id: uuid.UUID
    issue_update_id: uuid.UUID | None
    original_filename: str
    stored_filename: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str | None
    description: str | None
    uploaded_by: uuid.UUID
    uploaded_at: datetime
    removed_at: datetime | None
    # NOTE: storage_path is intentionally NOT exposed.
