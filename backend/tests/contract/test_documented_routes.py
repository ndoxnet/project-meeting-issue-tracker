# Concept by MrHan (08974747477)
"""Guards against contract drift: the committed OpenAPI artifact and the
ENDPOINTS.md inventory must stay in sync with the live application."""

from __future__ import annotations

from pathlib import Path

from tests.contract.conftest import COMMITTED_OPENAPI, iter_operations

REPO_ROOT = COMMITTED_OPENAPI.parents[2]
ENDPOINTS_MD = REPO_ROOT / "docs" / "api" / "ENDPOINTS.md"


def test_committed_openapi_not_stale(schema, committed_schema) -> None:
    """docs/api/openapi.json must equal the live schema.

    If this fails, run `make openapi-export` and commit the result.
    """
    assert schema == committed_schema, (
        "Committed docs/api/openapi.json is stale — run `make openapi-export`."
    )


def test_endpoints_doc_covers_all_paths(committed_schema) -> None:
    assert ENDPOINTS_MD.is_file(), f"{ENDPOINTS_MD} missing"
    text = ENDPOINTS_MD.read_text()
    missing = [p for p in committed_schema["paths"] if p not in text]
    assert not missing, f"paths not documented in ENDPOINTS.md: {missing}"


def test_endpoints_doc_has_no_removed_paths(committed_schema) -> None:
    """Every /api path token in ENDPOINTS.md must exist in the schema (no ghosts)."""
    import re

    text = Path(ENDPOINTS_MD).read_text()
    documented = set(re.findall(r"`(/api/[^`]+)`", text))
    actual = set(committed_schema["paths"])
    # A documented token is a ghost only if it is neither an exact path nor a
    # prefix of one (base-path mentions like `/api/v1` are legitimate).
    ghosts = {
        d
        for d in documented
        if d not in actual and not any(a == d or a.startswith(d + "/") for a in actual)
    }
    assert not ghosts, f"ENDPOINTS.md references non-existent paths: {ghosts}"


def test_operation_ids_documented(committed_schema) -> None:
    text = ENDPOINTS_MD.read_text()
    missing = [
        op["operationId"]
        for _p, _m, op in iter_operations(committed_schema)
        if op["operationId"] not in text
    ]
    assert not missing, f"operationIds not documented in ENDPOINTS.md: {missing}"
