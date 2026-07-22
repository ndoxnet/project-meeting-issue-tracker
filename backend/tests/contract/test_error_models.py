# Concept by MrHan (08974747477)
from __future__ import annotations

from tests.contract.conftest import iter_operations


def test_error_envelope_shape(schema) -> None:
    schemas = schema["components"]["schemas"]
    assert "ErrorResponse" in schemas and "ErrorBody" in schemas
    body = schemas["ErrorBody"]["properties"]
    assert set(body) >= {"code", "message", "request_id"}


def test_attachment_upload_is_multipart(schema) -> None:
    op = schema["paths"]["/api/v1/issues/{issue_id}/attachments"]["post"]
    content = op["requestBody"]["content"]
    assert "multipart/form-data" in content


def test_csv_export_advertises_csv(schema) -> None:
    op = schema["paths"]["/api/v1/reports/issues.csv"]["get"]
    # The endpoint returns a raw CSV Response; at minimum it must be documented as
    # a 200 operation under the Reports tag with the reports_ prefix.
    assert "200" in op["responses"]
    assert op["tags"] == ["Reports"]
    assert op["operationId"] == "reports_issues_csv"


def test_attachment_download_present(schema) -> None:
    op = schema["paths"]["/api/v1/issues/{issue_id}/attachments/{attachment_id}/download"]["get"]
    assert op["operationId"] == "attachments_download"


def test_list_endpoints_use_page_models(schema) -> None:
    # Register/users/master-data list endpoints return a Page_* model.
    list_ops = {
        "users_list",
        "issues_list",
        "categories_list",
        "responsible_parties_list",
        "meetings_list",
        "meeting_occurrences_list",
    }
    seen = {}
    for _p, _m, op in iter_operations(schema):
        if op["operationId"] in list_ops:
            ref = op["responses"]["200"]["content"]["application/json"]["schema"].get("$ref", "")
            seen[op["operationId"]] = ref
    for oid, ref in seen.items():
        assert "Page_" in ref, f"{oid} does not return a Page_* model ({ref})"
    assert set(seen) == list_ops
