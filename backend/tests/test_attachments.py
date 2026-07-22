# Concept by MrHan (08974747477)
from __future__ import annotations

import pytest

from tests.conftest import auth_header, issue_payload

pytestmark = pytest.mark.asyncio
ISSUES = "/api/v1/issues"

PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n%%EOF\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 32


async def _new_issue(client, user, category) -> str:
    r = await client.post(ISSUES, json=issue_payload(category.id), headers=auth_header(user))
    return r.json()["issue"]["id"]


async def _upload(client, user, iid, *, filename, content, mime):
    return await client.post(
        f"{ISSUES}/{iid}/attachments",
        files={"file": (filename, content, mime)},
        headers=auth_header(user),
    )


async def test_upload_pdf_valid(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _upload(
        client, editor_user, iid, filename="doc.pdf", content=PDF, mime="application/pdf"
    )
    assert r.status_code == 201
    body = r.json()
    assert body["mime_type"] == "application/pdf"
    assert body["checksum_sha256"] and len(body["checksum_sha256"]) == 64
    # Stored filename is randomized (not the original).
    assert body["stored_filename"] != "doc.pdf"
    assert "storage_path" not in body


async def test_upload_png_and_jpeg(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r1 = await _upload(client, editor_user, iid, filename="i.png", content=PNG, mime="image/png")
    r2 = await _upload(client, editor_user, iid, filename="i.jpg", content=JPEG, mime="image/jpeg")
    assert r1.status_code == 201 and r2.status_code == 201


async def test_wrong_signature_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    # Declares PDF but content is PNG bytes.
    r = await _upload(
        client, editor_user, iid, filename="fake.pdf", content=PNG, mime="application/pdf"
    )
    assert r.status_code == 415
    assert r.json()["error"]["code"] == "ATTACHMENT_CONTENT_MISMATCH"


async def test_disallowed_type_rejected(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _upload(
        client, editor_user, iid, filename="a.txt", content=b"hello", mime="text/plain"
    )
    assert r.status_code == 415
    assert r.json()["error"]["code"] == "ATTACHMENT_TYPE_NOT_ALLOWED"


async def test_size_limit(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    big = PDF + b"\x00" * (1 * 1024 * 1024 + 10)  # > 1 MB test cap
    r = await _upload(
        client, editor_user, iid, filename="big.pdf", content=big, mime="application/pdf"
    )
    assert r.status_code == 413
    assert r.json()["error"]["code"] == "ATTACHMENT_TOO_LARGE"


async def test_path_traversal_filename_sanitized(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _upload(
        client,
        editor_user,
        iid,
        filename="../../etc/passwd.pdf",
        content=PDF,
        mime="application/pdf",
    )
    assert r.status_code == 201
    name = r.json()["original_filename"]
    assert "/" not in name and ".." not in name


async def test_viewer_cannot_upload(client, viewer_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    r = await _upload(
        client, viewer_user, iid, filename="d.pdf", content=PDF, mime="application/pdf"
    )
    assert r.status_code == 403


async def test_viewer_can_download(client, viewer_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    up = await _upload(
        client, editor_user, iid, filename="d.pdf", content=PDF, mime="application/pdf"
    )
    aid = up.json()["id"]
    r = await client.get(
        f"{ISSUES}/{iid}/attachments/{aid}/download", headers=auth_header(viewer_user)
    )
    assert r.status_code == 200
    assert r.content == PDF


async def test_unauthenticated_download_blocked(client, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    up = await _upload(
        client, editor_user, iid, filename="d.pdf", content=PDF, mime="application/pdf"
    )
    aid = up.json()["id"]
    r = await client.get(f"{ISSUES}/{iid}/attachments/{aid}/download")
    assert r.status_code == 401


async def test_remove_admin_only_and_soft(client, admin_user, editor_user, category) -> None:
    iid = await _new_issue(client, editor_user, category)
    up = await _upload(
        client, editor_user, iid, filename="d.pdf", content=PDF, mime="application/pdf"
    )
    aid = up.json()["id"]
    # editor forbidden
    r_forbidden = await client.post(
        f"{ISSUES}/{iid}/attachments/{aid}/remove", headers=auth_header(editor_user)
    )
    assert r_forbidden.status_code == 403
    # admin removes (soft)
    r_ok = await client.post(
        f"{ISSUES}/{iid}/attachments/{aid}/remove", headers=auth_header(admin_user)
    )
    assert r_ok.status_code == 200
    # No longer listed; download now 404.
    listed = await client.get(f"{ISSUES}/{iid}/attachments", headers=auth_header(admin_user))
    assert all(a["id"] != aid for a in listed.json())
    dl = await client.get(
        f"{ISSUES}/{iid}/attachments/{aid}/download", headers=auth_header(admin_user)
    )
    assert dl.status_code == 404
