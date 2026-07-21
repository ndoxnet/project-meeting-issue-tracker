# Concept by MrHan (08974747477)
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.tokens import TokenError, create_access_token, decode_access_token


def _settings():
    return get_settings()


def test_valid_token_roundtrip() -> None:
    uid = uuid.uuid4()
    token, expires_in = create_access_token(user_id=uid, role="ADMIN")
    data = decode_access_token(token)
    assert data.sub == str(uid)
    assert data.role == "ADMIN"
    assert data.token_type == "access"
    assert expires_in > 0


def test_expired_token_rejected() -> None:
    s = _settings()
    now = datetime.now(UTC) - timedelta(hours=2)
    payload = {
        "sub": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=1)).timestamp()),
        "jti": uuid.uuid4().hex,
        "type": "access",
    }
    token = jwt.encode(payload, s.SECRET_KEY, algorithm=s.JWT_ALGORITHM)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_wrong_signature_rejected() -> None:
    s = _settings()
    payload = {
        "sub": str(uuid.uuid4()),
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int((datetime.now(UTC) + timedelta(minutes=10)).timestamp()),
        "jti": uuid.uuid4().hex,
        "type": "access",
    }
    token = jwt.encode(payload, "a-different-secret-key-value-000000", algorithm=s.JWT_ALGORITHM)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_malformed_token_rejected() -> None:
    with pytest.raises(TokenError):
        decode_access_token("not.a.jwt")


def test_missing_subject_rejected() -> None:
    s = _settings()
    payload = {
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int((datetime.now(UTC) + timedelta(minutes=10)).timestamp()),
        "jti": uuid.uuid4().hex,
        "type": "access",
    }
    token = jwt.encode(payload, s.SECRET_KEY, algorithm=s.JWT_ALGORITHM)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_wrong_token_type_rejected() -> None:
    s = _settings()
    payload = {
        "sub": str(uuid.uuid4()),
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int((datetime.now(UTC) + timedelta(minutes=10)).timestamp()),
        "jti": uuid.uuid4().hex,
        "type": "refresh",
    }
    token = jwt.encode(payload, s.SECRET_KEY, algorithm=s.JWT_ALGORITHM)
    with pytest.raises(TokenError):
        decode_access_token(token)
