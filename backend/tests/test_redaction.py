# Concept by MrHan (08974747477)
from __future__ import annotations

from app.core.redaction import REDACTED, redact


def test_redacts_top_level_sensitive_keys() -> None:
    out = redact({"username": "bob", "password": "secret", "token": "abc"})
    assert out["username"] == "bob"
    assert out["password"] == REDACTED
    assert out["token"] == REDACTED


def test_redacts_nested_and_lists() -> None:
    out = redact(
        {
            "user": {"name": "bob", "password_hash": "$argon2..."},
            "items": [{"access_token": "xyz"}, {"ok": 1}],
        }
    )
    assert out["user"]["name"] == "bob"
    assert out["user"]["password_hash"] == REDACTED
    assert out["items"][0]["access_token"] == REDACTED
    assert out["items"][1]["ok"] == 1


def test_scalars_pass_through() -> None:
    assert redact(5) == 5
    assert redact("plain") == "plain"
