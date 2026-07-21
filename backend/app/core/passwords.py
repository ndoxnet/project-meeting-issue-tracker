# Concept by MrHan (08974747477)
"""Password hashing and policy (Argon2 via pwdlib — see ADR-008).

Never logs passwords or hashes. Uses a dummy hash to keep verification timing
similar for unknown users (reduces username enumeration via timing).
"""
from __future__ import annotations

from pwdlib import PasswordHash

# Minimum/maximum bounds. The max bounds resource use; Argon2 has no low limit,
# but we require a reasonable minimum length for the MVP policy.
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

_password_hash = PasswordHash.recommended()

# Precomputed dummy hash to verify against when a user is not found, so the code
# path (and timing) is similar whether or not the username exists.
_DUMMY_HASH = _password_hash.hash("dummy-password-not-a-secret-000000")


class PasswordPolicyError(ValueError):
    """Raised when a candidate password violates the documented policy."""


def validate_password_policy(
    password: str, *, username: str | None = None, email: str | None = None
) -> None:
    """Enforce the MVP password policy. Raises PasswordPolicyError on violation.

    Policy: 12–128 chars; not equal (case-insensitive) to username or email.
    Complex character-class rules are intentionally not forced. Breached-password
    lookup is NOT implemented in the MVP (documented in docs/SECURITY.md).
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters."
        )
    low = password.strip().lower()
    if username and low == username.strip().lower():
        raise PasswordPolicyError("Password must not equal the username.")
    if email and low == email.strip().lower():
        raise PasswordPolicyError("Password must not equal the email.")


def hash_password(password: str) -> str:
    """Hash a password with Argon2. Input length is bounded to prevent abuse."""
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters."
        )
    return _password_hash.hash(password)


def verify_password(plain_password: str, password_hash: str | None) -> bool:
    """Verify a password against a stored hash.

    If ``password_hash`` is None (unknown user), still perform a dummy verify to
    equalize timing, then return False. Overlong input is rejected fast.
    """
    if len(plain_password) > MAX_PASSWORD_LENGTH:
        return False
    if not password_hash:
        _password_hash.verify(plain_password, _DUMMY_HASH)
        return False
    try:
        return _password_hash.verify(plain_password, password_hash)
    except Exception:
        return False


def verify_and_update_password(
    plain_password: str, password_hash: str | None
) -> tuple[bool, str | None]:
    """Verify and, if the hash params are outdated, return an upgraded hash.

    Returns (is_valid, new_hash_or_None). ``new_hash`` is non-None only when the
    caller should persist a rehashed value.
    """
    if len(plain_password) > MAX_PASSWORD_LENGTH:
        return (False, None)
    if not password_hash:
        _password_hash.verify(plain_password, _DUMMY_HASH)
        return (False, None)
    try:
        valid, updated = _password_hash.verify_and_update(plain_password, password_hash)
    except Exception:
        return (False, None)
    return (valid, updated)
