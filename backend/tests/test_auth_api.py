# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from tests.conftest import auth_header, make_user

pytestmark = pytest.mark.asyncio

LOGIN = "/api/v1/auth/login"


async def test_login_success(client, admin_user) -> None:
    resp = await client.post(LOGIN, json={"username": "admin", "password": "ValidPassw0rd!!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["username"] == "admin"
    assert "password_hash" not in body["user"]


async def test_login_with_email(client, admin_user) -> None:
    resp = await client.post(
        LOGIN, json={"username": "admin@example.com", "password": "ValidPassw0rd!!"}
    )
    assert resp.status_code == 200


async def test_login_wrong_password(client, admin_user) -> None:
    resp = await client.post(LOGIN, json={"username": "admin", "password": "WrongPassword12"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"


async def test_login_unknown_user(client) -> None:
    resp = await client.post(LOGIN, json={"username": "ghost", "password": "whatever12345"})
    assert resp.status_code == 401


async def test_login_inactive_user(client, sessionmaker) -> None:
    await make_user(sessionmaker, username="dormant", role=UserRole.EDITOR, is_active=False)
    resp = await client.post(LOGIN, json={"username": "dormant", "password": "ValidPassw0rd!!"})
    assert resp.status_code == 401


async def test_me_valid(client, admin_user) -> None:
    resp = await client.get("/api/v1/auth/me", headers=auth_header(admin_user))
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


async def test_me_invalid_token(client) -> None:
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


async def test_me_no_token(client) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_viewer_forbidden_from_admin_route(client, viewer_user) -> None:
    resp = await client.get("/api/v1/users", headers=auth_header(viewer_user))
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "AUTHORIZATION_FAILED"


async def test_request_id_echoed(client, admin_user) -> None:
    resp = await client.get(
        "/api/v1/auth/me",
        headers={**auth_header(admin_user), "X-Request-ID": "req-abc-123"},
    )
    assert resp.headers.get("X-Request-ID") == "req-abc-123"


async def test_login_success_audited(client, admin_user, sessionmaker) -> None:
    await client.post(LOGIN, json={"username": "admin", "password": "ValidPassw0rd!!"})
    async with sessionmaker() as s:
        rows = (
            await s.execute(select(AuditLog).where(AuditLog.action == "auth.login_success"))
        ).scalars().all()
    assert len(rows) == 1
    assert rows[0].actor_user_id == admin_user.id


async def test_login_failure_audited_without_password(client, admin_user, sessionmaker) -> None:
    await client.post(LOGIN, json={"username": "admin", "password": "WrongPassword12"})
    async with sessionmaker() as s:
        rows = (
            await s.execute(select(AuditLog).where(AuditLog.action == "auth.login_failed"))
        ).scalars().all()
    assert len(rows) == 1
    # Actor is null on failed login; payload must not contain the password.
    assert rows[0].actor_user_id is None
    assert "password" not in (rows[0].after_data or {})
