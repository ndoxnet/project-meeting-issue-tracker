# Concept by MrHan (08974747477)
"""Per-request context (request id, client IP, user agent) for audit/logging."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


@dataclass(frozen=True)
class RequestContext:
    request_id: str | None
    ip_address: str | None
    user_agent: str | None


def get_request_context(request: Request) -> RequestContext:
    return RequestContext(
        request_id=getattr(request.state, "request_id", None),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
