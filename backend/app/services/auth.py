# Concept by MrHan (08974747477)
"""Authentication service: login, logout audit.

Never stores or logs raw tokens or passwords. Failed logins are audited with a
null actor and no password material. The audit row is committed together with any
state change (or on its own for a failed attempt).
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.errors import AuthenticationError
from app.core.passwords import verify_and_update_password
from app.core.tokens import create_access_token
from app.models.user import User
from app.repositories import user as user_repo
from app.services.audit import record_audit


async def authenticate(
    session: AsyncSession,
    *,
    identifier: str,
    password: str,
    ctx: RequestContext,
) -> tuple[User, str, int]:
    """Authenticate and return (user, access_token, expires_in).

    Raises AuthenticationError (generic) for unknown user, wrong password, or
    inactive account. Timing is equalized for unknown users via a dummy verify.
    """
    user = await user_repo.get_by_login(session, identifier)

    stored_hash = user.password_hash if user else None
    valid, new_hash = verify_and_update_password(password, stored_hash)

    if user is None or not valid or not user.is_active:
        record_audit(
            session,
            action="auth.login_failed",
            entity_type="user",
            entity_id=user.id if user else None,
            actor_user_id=None,
            after={"identifier": identifier, "reason": _fail_reason(user, valid)},
            ctx=ctx,
        )
        await session.commit()
        raise AuthenticationError("Invalid credentials")

    # Optionally upgrade the stored hash if params changed.
    if new_hash:
        user.password_hash = new_hash

    user.last_login_at = datetime.now(UTC)
    token, expires_in = create_access_token(user_id=user.id, role=user.role)

    record_audit(
        session,
        action="auth.login_success",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=user.id,
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(user)
    return user, token, expires_in


async def record_logout(
    session: AsyncSession, *, user: User, ctx: RequestContext
) -> None:
    """Audit a logout. Server-side token revocation is NOT implemented (MVP);
    the client is responsible for discarding the token."""
    record_audit(
        session,
        action="auth.logout",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=user.id,
        ctx=ctx,
    )
    await session.commit()


def _fail_reason(user: User | None, valid: bool) -> str:
    if user is None:
        return "unknown_user"
    if not valid:
        return "bad_password"
    if not user.is_active:
        return "inactive"
    return "unknown"
