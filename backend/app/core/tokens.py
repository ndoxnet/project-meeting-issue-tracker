# Concept by MrHan (08974747477)
"""JWT access-token service (PyJWT, HS256 — see ADR-009).

Tokens carry sub, iat, exp, jti, role, and type=access. Decoding always passes an
explicit algorithm allow-list — the algorithm is never read from the token.
Invalid tokens raise a single generic error type; details are not leaked to
clients. Token values are never logged.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings

TOKEN_TYPE = "access"


class TokenError(Exception):
    """Generic token failure (expired, malformed, bad signature, missing sub)."""


@dataclass(frozen=True)
class TokenData:
    sub: str
    role: str | None
    jti: str
    token_type: str


def create_access_token(
    *, user_id: str | uuid.UUID, role: str | None = None
) -> tuple[str, int]:
    """Create a signed access token. Returns (token, expires_in_seconds)."""
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
        "type": TOKEN_TYPE,
    }
    if role is not None:
        payload["role"] = role
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return token, expires_in


def decode_access_token(token: str) -> TokenData:
    """Decode and validate an access token. Raises TokenError on any problem.

    Algorithm is fixed by settings and passed explicitly to ``jwt.decode`` — the
    token's own ``alg`` header is never trusted.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp", "jti"]},
        )
    except jwt.PyJWTError as exc:
        # Do not leak whether it was expired vs malformed vs bad signature.
        raise TokenError("Invalid authentication token") from exc

    if payload.get("type") != TOKEN_TYPE:
        raise TokenError("Invalid token type")

    sub = payload.get("sub")
    if not sub:
        raise TokenError("Token missing subject")

    return TokenData(
        sub=str(sub),
        role=payload.get("role"),
        jti=str(payload.get("jti")),
        token_type=str(payload.get("type")),
    )
