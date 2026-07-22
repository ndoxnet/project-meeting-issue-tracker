# Concept by MrHan (08974747477)
from __future__ import annotations

import json

from tests.contract.conftest import iter_operations

INTERNAL_FIELDS = ["password_hash", "storage_path", "secret_key", "SECRET_KEY"]


def test_openapi_generates_and_is_valid(schema) -> None:
    assert schema["openapi"].startswith("3.")
    assert "paths" in schema and schema["paths"]
    assert schema["info"]["version"] == "0.2.0"
    assert schema["info"]["title"]
    # Round-trips as JSON.
    json.dumps(schema)


def test_expected_operation_count(schema) -> None:
    ops = list(iter_operations(schema))
    assert len(ops) == 63  # update deliberately when endpoints change (ADR/contract)


def test_no_internal_fields_exposed(schema) -> None:
    blob = json.dumps(schema)
    for field in INTERNAL_FIELDS:
        assert field not in blob, f"internal field '{field}' leaked into OpenAPI"


def test_error_response_schema_present(schema) -> None:
    schemas = schema["components"]["schemas"]
    assert "ErrorResponse" in schemas
    err = schemas["ErrorResponse"]["properties"]["error"]
    # Envelope: {"error": {"code","message","request_id"}}
    assert "$ref" in err or "allOf" in err


def test_pagination_model_consistent(schema) -> None:
    schemas = schema["components"]["schemas"]
    # Generic Page[T] models expose items + meta with the PageMeta shape.
    page_models = [n for n in schemas if n.startswith("Page_")]
    assert page_models, "no Page_* pagination models found"
    for name in page_models:
        props = schemas[name]["properties"]
        assert "items" in props and "meta" in props
    meta = schemas["PageMeta"]["properties"]
    assert set(meta) == {"page", "page_size", "total", "pages"}


def test_enums_present(schema) -> None:
    schemas = schema["components"]["schemas"]
    assert set(schemas["IssueStatus"]["enum"]) == {
        "OPEN",
        "IN_PROGRESS",
        "PENDING",
        "CLOSED",
        "REOPENED",
    }
    assert set(schemas["IssuePriority"]["enum"]) == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert set(schemas["UserRole"]["enum"]) == {"ADMIN", "EDITOR", "VIEWER"}


def test_tags_are_canonical(schema) -> None:
    names = {t["name"] for t in schema.get("tags", [])}
    expected = {
        "Health",
        "Authentication",
        "Users",
        "Categories",
        "Responsible Parties",
        "Meetings",
        "Meeting Occurrences",
        "Issues",
        "Issue Updates",
        "Attachments",
        "Dashboard",
        "Reports",
        "Settings",
    }
    assert expected.issubset(names)
    # Every operation uses exactly one canonical tag.
    for _p, _m, op in iter_operations(schema):
        assert len(op.get("tags", [])) == 1
        assert op["tags"][0] in expected
