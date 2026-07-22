# Concept by MrHan (08974747477)
"""Request-ID middleware.

Accepts a client-provided X-Request-ID when it is a sane, bounded value;
otherwise generates a UUID. Stores it on request.state and echoes it on the
response so it can be correlated with audit logs and structured access logs.
"""

from __future__ import annotations

import re
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HEADER = "X-Request-ID"
_MAX_LEN = 64
# Conservative allow-list: identifiers and dashes only.
_VALID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _sanitize(value: str | None) -> str:
    if value and len(value) <= _MAX_LEN and _VALID.match(value):
        return value
    return uuid.uuid4().hex


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = _sanitize(request.headers.get(HEADER))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[HEADER] = request_id
        return response
