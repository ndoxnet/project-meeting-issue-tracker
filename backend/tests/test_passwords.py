# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from app.core.passwords import (
    MAX_PASSWORD_LENGTH,
    PasswordPolicyError,
    hash_password,
    validate_password_policy,
    verify_password,
)


def test_hash_differs_from_plaintext() -> None:
    h = hash_password("CorrectHorse12")
    assert h != "CorrectHorse12"
    assert h.startswith("$argon2")


def test_verify_correct() -> None:
    h = hash_password("CorrectHorse12")
    assert verify_password("CorrectHorse12", h) is True


def test_verify_incorrect() -> None:
    h = hash_password("CorrectHorse12")
    assert verify_password("WrongPassword12", h) is False


def test_verify_none_hash_is_false() -> None:
    # Unknown user path: dummy verify then False (no exception).
    assert verify_password("anything-here", None) is False


def test_policy_too_short() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_policy("short")


def test_policy_too_long() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_policy("a" * (MAX_PASSWORD_LENGTH + 1))


def test_policy_equals_username_rejected() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_policy("johndoe12345", username="JohnDoe12345")


def test_long_input_rejected_on_verify() -> None:
    h = hash_password("CorrectHorse12")
    assert verify_password("a" * (MAX_PASSWORD_LENGTH + 1), h) is False
