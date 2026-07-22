# Concept by MrHan (08974747477)
"""Create the initial ADMIN user from environment variables.

Idempotent: if an active admin (by username or email) already exists, it does
nothing and never changes an existing admin's password. Fails loudly if the
credentials are still CHANGE_ME placeholders. Never prints the password.

Run manually (developer machine / deploy step) — NOT against production in 2A:
    python -m scripts.bootstrap_admin
"""

from __future__ import annotations

import asyncio
import sys

from app.core.config import PLACEHOLDER, get_settings
from app.core.passwords import PasswordPolicyError, hash_password, validate_password_policy
from app.db.session import dispose_engine, get_sessionmaker
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import user as user_repo


async def _run() -> int:
    settings = get_settings()
    email = settings.ADMIN_EMAIL.strip().lower()
    username = settings.ADMIN_USERNAME.strip().lower()
    password = settings.ADMIN_INITIAL_PASSWORD

    if PLACEHOLDER in {settings.ADMIN_EMAIL, settings.ADMIN_USERNAME, password}:
        print("[bootstrap_admin] ERROR: ADMIN_* env still contains CHANGE_ME.")
        return 2
    try:
        validate_password_policy(password, username=username, email=email)
    except PasswordPolicyError as exc:
        print(f"[bootstrap_admin] ERROR: admin password policy: {exc}")
        return 2

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        if await user_repo.get_by_username(session, username) or await user_repo.get_by_email(
            session, email
        ):
            print("[bootstrap_admin] Admin already exists — no changes made.")
            return 0
        session.add(
            User(
                full_name="Administrator",
                email=email,
                username=username,
                password_hash=hash_password(password),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
        )
        await session.commit()
    print(f"[bootstrap_admin] Created admin '{username}'.")
    return 0


def main() -> None:
    try:
        code = asyncio.run(_run())
    finally:
        asyncio.run(dispose_engine())
    sys.exit(code)


if __name__ == "__main__":  # pragma: no cover
    main()
