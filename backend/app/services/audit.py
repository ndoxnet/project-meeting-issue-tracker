# Concept by MrHan (08974747477)
"""Audit logging foundation.

``record_audit`` stages an AuditLog row in the CURRENT session/transaction — it
does NOT commit. The calling service/endpoint commits once at its transaction
boundary, so the audit row and the business change succeed or fail together
(no half-successful operations). before/after payloads are redacted.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.redaction import redact
from app.models.audit_log import AuditLog


def record_audit(
    session: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | str | None = None,
    actor_user_id: uuid.UUID | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ctx: RequestContext | None = None,
) -> AuditLog:
    """Stage an audit record (no commit). Returns the pending AuditLog."""
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=_coerce_uuid(entity_id),
        before_data=redact(before) if before is not None else None,
        after_data=redact(after) if after is not None else None,
        request_id=ctx.request_id if ctx else None,
        ip_address=ctx.ip_address if ctx else None,
        user_agent=ctx.user_agent if ctx else None,
    )
    session.add(entry)
    return entry


def _coerce_uuid(value: uuid.UUID | str | None) -> uuid.UUID | None:
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None
