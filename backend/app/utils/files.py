# Concept by MrHan (08974747477)
"""Secure attachment helpers: filename sanitization, magic-byte sniffing,
and stored-path generation. No heavy OS dependency (no python-magic) — we use
simple, stable signature checks (documented limitation in SECURITY.md)."""

from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path

# Allowed MIME -> (list of magic-byte signatures, canonical extension)
_SIGNATURES: dict[str, tuple[tuple[bytes, ...], str]] = {
    "application/pdf": ((b"%PDF-",), "pdf"),
    "image/jpeg": ((b"\xff\xd8\xff",), "jpg"),
    "image/png": ((b"\x89PNG\r\n\x1a\n",), "png"),
}

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(name: str) -> str:
    """Reduce a user filename to a safe basename (no paths, no traversal)."""
    base = Path(name).name  # strip any directory components
    base = _SAFE_NAME.sub("_", base).strip("._") or "file"
    return base[:200]


def sniff_mime(head: bytes) -> str | None:
    """Return the MIME type if the leading bytes match a known signature."""
    for mime, (sigs, _ext) in _SIGNATURES.items():
        if any(head.startswith(sig) for sig in sigs):
            return mime
    return None


def signature_matches(declared_mime: str, head: bytes) -> bool:
    """True if the content signature matches the declared (allowed) MIME."""
    entry = _SIGNATURES.get(declared_mime)
    if entry is None:
        return False
    sigs, _ext = entry
    return any(head.startswith(sig) for sig in sigs)


def extension_for(mime: str) -> str:
    entry = _SIGNATURES.get(mime)
    return entry[1] if entry else "bin"


def generate_stored_filename(mime: str) -> str:
    """Random, collision-resistant stored filename with a canonical extension."""
    return f"{uuid.uuid4().hex}.{extension_for(mime)}"


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def issue_storage_dir(storage_root: str, issue_id: uuid.UUID) -> Path:
    """Per-issue storage directory. Path is derived from the issue UUID only —
    never from any user-provided value (prevents path traversal)."""
    return Path(storage_root) / "issues" / str(issue_id)
