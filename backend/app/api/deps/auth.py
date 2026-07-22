# Concept by MrHan (08974747477)
"""Authentication & authorization dependencies.

Authorization uses the CURRENT database role of the user (fetched fresh on every
request), not just the JWT claim — the database is the source of truth.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthenticationError, AuthorizationError
from app.core.tokens import TokenError, decode_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

# auto_error=False so we raise our own generic AuthenticationError.
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated")
    try:
        data = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(data.sub)
    except (TokenError, ValueError) as exc:
        raise AuthenticationError("Invalid authentication token") from exc

    user = await session.get(User, user_id)
    if user is None:
        raise AuthenticationError("Invalid authentication token")
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        # Inactive accounts cannot act, even with a still-valid token.
        raise AuthenticationError("Account is inactive")
    return user


def require_roles(*roles: UserRole) -> Callable[..., Awaitable[User]]:
    """Return a dependency that allows only the given roles (DB role is truth)."""
    allowed = {r.value for r in roles}

    async def _dep(user: User = Depends(get_current_active_user)) -> User:
        if user.role not in allowed:
            raise AuthorizationError("Insufficient permissions")
        return user

    return _dep


# Convenience dependencies.
require_admin = require_roles(UserRole.ADMIN)
require_editor = require_roles(UserRole.ADMIN, UserRole.EDITOR)
require_any = require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.VIEWER)
