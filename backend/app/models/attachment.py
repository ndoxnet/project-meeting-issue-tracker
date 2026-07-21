# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPKMixin


class Attachment(UUIDPKMixin, Base):
    __tablename__ = "attachments"
    __table_args__ = (
        CheckConstraint("size_bytes >= 0", name="size_non_negative"),
    )

    issue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("issues.id"), nullable=False, index=True
    )
    issue_update_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("issue_updates.id"), nullable=True
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(150), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    removed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
