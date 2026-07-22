# Concept by MrHan (08974747477)
"""User management service: create/update/activate/deactivate/reset-password.

Enforces uniqueness, password policy, and the last-active-admin safety rule.
Every mutation writes an audit row and commits atomically with the change.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.context import RequestContext
from app.core.errors import ConflictError, DomainValidationError, NotFoundError
from app.core.passwords import PasswordPolicyError, hash_password, validate_password_policy
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import user as user_repo
from app.schemas.user import UserCreate, UserUpdate
from app.services.audit import record_audit


def _public(user: User) -> dict:
    """Audit-safe projection of a user (no password hash)."""
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
    }


async def create_user(
    session: AsyncSession, *, data: UserCreate, actor: User, ctx: RequestContext
) -> User:
    if await user_repo.get_by_username(session, data.username):
        raise ConflictError("Username already exists")
    if await user_repo.get_by_email(session, data.email):
        raise ConflictError("Email already exists")
    try:
        validate_password_policy(data.password, username=data.username, email=data.email)
    except PasswordPolicyError as exc:
        raise DomainValidationError(str(exc)) from exc

    user = User(
        full_name=data.full_name,
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role.value,
        is_active=True,
    )
    session.add(user)
    await session.flush()  # assign id
    record_audit(
        session,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=actor.id,
        after=_public(user),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    data: UserUpdate,
    actor: User,
    ctx: RequestContext,
) -> User:
    user = await user_repo.get_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")

    before = _public(user)

    if data.email is not None and data.email != user.email:
        existing = await user_repo.get_by_email(session, data.email)
        if existing and existing.id != user.id:
            raise ConflictError("Email already exists")
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None and data.role.value != user.role:
        # Guard: don't demote the only remaining active admin.
        if user.role == UserRole.ADMIN.value and data.role != UserRole.ADMIN:
            if await user_repo.count_active_admins(session) <= 1 and user.is_active:
                raise DomainValidationError("Cannot change role of the only active admin")
        user.role = data.role.value

    record_audit(
        session,
        action="user.update",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=actor.id,
        before=before,
        after=_public(user),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(user)
    return user


async def set_active(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    active: bool,
    actor: User,
    ctx: RequestContext,
) -> User:
    user = await user_repo.get_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not active:
        # Cannot deactivate the only active admin (whoever performs it).
        if user.role == UserRole.ADMIN.value and user.is_active:
            if await user_repo.count_active_admins(session) <= 1:
                raise DomainValidationError("Cannot deactivate the only active admin")

    before = _public(user)
    user.is_active = active
    record_audit(
        session,
        action="user.activate" if active else "user.deactivate",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=actor.id,
        before=before,
        after=_public(user),
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(user)
    return user


async def reset_password(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    new_password: str,
    actor: User,
    ctx: RequestContext,
) -> User:
    user = await user_repo.get_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")
    try:
        validate_password_policy(new_password, username=user.username, email=user.email)
    except PasswordPolicyError as exc:
        raise DomainValidationError(str(exc)) from exc

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(UTC)  # touch (mixin also handles onupdate)
    # Audit records the action only — never the password or its hash.
    record_audit(
        session,
        action="user.reset_password",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=actor.id,
        after={"id": str(user.id), "password_changed": True},
        ctx=ctx,
    )
    await session.commit()
    await session.refresh(user)
    return user
