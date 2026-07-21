# Concept by MrHan (08974747477)
"""Recursive redaction for audit/log payloads.

Any key whose (lowercased) name matches a sensitive term is replaced with a
constant marker. Applied before writing audit before/after data and before any
structured logging of request context.
"""
from __future__ import annotations

from typing import Any

REDACTED = "[REDACTED]"

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "access_token",
        "authorization",
        "secret",
        "secret_key",
        "token",
        "admin_initial_password",
    }
)


def _is_sensitive(key: str) -> bool:
    k = key.lower()
    return any(term in k for term in SENSITIVE_KEYS)


def redact(value: Any) -> Any:
    """Return a redacted deep copy of dicts/lists; scalars pass through."""
    if isinstance(value, dict):
        return {
            k: (REDACTED if _is_sensitive(str(k)) else redact(v))
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return value
