# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from app.models.enums import UserRole
from tests.conftest import auth_header, make_user

pytestmark = pytest.mark.asyncio

USERS = "/api/v1/users"


def _new_user_payload(**over):
    base = {
        "full_name": "New Person",
        "email": "new.person@example.com",
        "username": "newperson",
        "role": "EDITOR",
        "password": "BrandNewPass12",
    }
    base.update(over)
    return base


async def test_create_user(client, admin_user) -> None:
    resp = await client.post(USERS, json=_new_user_payload(), headers=auth_header(admin_user))
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "newperson"
    assert body["is_active"] is True
    assert "password" not in body and "password_hash" not in body


async def test_create_duplicate_username(client, admin_user) -> None:
    await client.post(USERS, json=_new_user_payload(), headers=auth_header(admin_user))
    resp = await client.post(
        USERS,
        json=_new_user_payload(email="other@example.com"),
        headers=auth_header(admin_user),
    )
    assert resp.status_code == 409


async def test_create_duplicate_email_case_insensitive(client, admin_user) -> None:
    await client.post(USERS, json=_new_user_payload(), headers=auth_header(admin_user))
    resp = await client.post(
        USERS,
        json=_new_user_payload(username="another", email="NEW.PERSON@example.com"),
        headers=auth_header(admin_user),
    )
    assert resp.status_code == 409


async def test_create_user_weak_password_rejected(client, admin_user) -> None:
    resp = await client.post(
        USERS, json=_new_user_payload(password="short"), headers=auth_header(admin_user)
    )
    assert resp.status_code in (400, 422)


async def test_list_users_paginated(client, admin_user) -> None:
    resp = await client.get(f"{USERS}?page=1&page_size=10", headers=auth_header(admin_user))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body and "meta" in body
    assert body["meta"]["page"] == 1


async def test_search_users(client, admin_user, sessionmaker) -> None:
    await make_user(sessionmaker, username="charlie", role=UserRole.VIEWER)
    resp = await client.get(f"{USERS}?search=charlie", headers=auth_header(admin_user))
    assert resp.status_code == 200
    usernames = [u["username"] for u in resp.json()["items"]]
    assert "charlie" in usernames


async def test_deactivate_and_activate(client, admin_user, sessionmaker) -> None:
    target = await make_user(sessionmaker, username="target", role=UserRole.EDITOR)
    r1 = await client.post(f"{USERS}/{target.id}/deactivate", headers=auth_header(admin_user))
    assert r1.status_code == 200 and r1.json()["is_active"] is False
    r2 = await client.post(f"{USERS}/{target.id}/activate", headers=auth_header(admin_user))
    assert r2.status_code == 200 and r2.json()["is_active"] is True


async def test_role_update(client, admin_user, sessionmaker) -> None:
    target = await make_user(sessionmaker, username="promote", role=UserRole.VIEWER)
    resp = await client.patch(
        f"{USERS}/{target.id}", json={"role": "EDITOR"}, headers=auth_header(admin_user)
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "EDITOR"


async def test_prevent_deactivating_only_admin(client, admin_user) -> None:
    # admin_user is the only active admin; deactivation must be refused.
    resp = await client.post(
        f"{USERS}/{admin_user.id}/deactivate", headers=auth_header(admin_user)
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_reset_password(client, admin_user, sessionmaker) -> None:
    target = await make_user(sessionmaker, username="resetme", role=UserRole.EDITOR)
    resp = await client.post(
        f"{USERS}/{target.id}/reset-password",
        json={"new_password": "AFreshPass1234"},
        headers=auth_header(admin_user),
    )
    assert resp.status_code == 200
    # New password works for login.
    login = await client.post(
        "/api/v1/auth/login", json={"username": "resetme", "password": "AFreshPass1234"}
    )
    assert login.status_code == 200


async def test_editor_cannot_create_user(client, editor_user) -> None:
    resp = await client.post(USERS, json=_new_user_payload(), headers=auth_header(editor_user))
    assert resp.status_code == 403
