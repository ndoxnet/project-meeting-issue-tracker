# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings

VALID_SECRET = "x" * 40


def test_production_rejects_debug() -> None:
    with pytest.raises(ValidationError):
        Settings(APP_ENV="production", DEBUG=True, SECRET_KEY=VALID_SECRET)


def test_placeholder_secret_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="CHANGE_ME")


def test_short_secret_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="tooshort")


def test_invalid_jwt_algorithm_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY=VALID_SECRET, JWT_ALGORITHM="none")


def test_invalid_timezone_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY=VALID_SECRET, DISPLAY_TIMEZONE="Mars/Phobos")


def test_list_parsing() -> None:
    s = Settings(
        SECRET_KEY=VALID_SECRET,
        ALLOWED_ORIGINS="http://a.test, http://b.test ,",
        ATTACHMENT_ALLOWED_TYPES="application/pdf, image/png",
    )
    assert s.allowed_origins_list == ["http://a.test", "http://b.test"]
    assert s.attachment_allowed_types_list == ["application/pdf", "image/png"]


def test_production_debug_false_ok() -> None:
    s = Settings(APP_ENV="production", DEBUG=False, SECRET_KEY=VALID_SECRET)
    assert s.is_production is True
