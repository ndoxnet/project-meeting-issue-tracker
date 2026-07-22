# Concept by MrHan (08974747477)
"""Shared helpers for contract tests: the live app OpenAPI schema and the
committed artifact, plus the set of public operationIds."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.main import app

# Endpoints intentionally reachable without authentication.
PUBLIC_OPERATION_IDS = {"health_check", "meta_ping", "auth_login"}

REPO_ROOT = Path(__file__).resolve().parents[3]
COMMITTED_OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"


@pytest.fixture(scope="session")
def schema() -> dict:
    """Freshly generated OpenAPI schema from the live app."""
    return app.openapi()


@pytest.fixture(scope="session")
def committed_schema() -> dict:
    assert COMMITTED_OPENAPI.is_file(), f"{COMMITTED_OPENAPI} missing — run `make openapi-export`."
    return json.loads(COMMITTED_OPENAPI.read_text())


def iter_operations(schema: dict):
    for path, methods in schema["paths"].items():
        for method, op in methods.items():
            if method in {"get", "post", "put", "patch", "delete"}:
                yield path, method, op
