# Concept by MrHan (08974747477)
from __future__ import annotations

from tests.contract.conftest import PUBLIC_OPERATION_IDS, iter_operations


def test_bearer_scheme_declared(schema) -> None:
    schemes = schema["components"].get("securitySchemes", {})
    assert "HTTPBearer" in schemes
    assert schemes["HTTPBearer"]["scheme"] == "bearer"


def test_public_endpoints_have_no_security(schema) -> None:
    for _p, _m, op in iter_operations(schema):
        if op["operationId"] in PUBLIC_OPERATION_IDS:
            assert not op.get("security"), f"{op['operationId']} should be public"


def test_protected_endpoints_declare_bearer(schema) -> None:
    for _p, _m, op in iter_operations(schema):
        oid = op["operationId"]
        if oid in PUBLIC_OPERATION_IDS:
            continue
        security = op.get("security")
        assert security, f"{oid} must declare security"
        assert any("HTTPBearer" in entry for entry in security), oid


def test_public_set_is_exactly_expected(schema) -> None:
    public = {op["operationId"] for _p, _m, op in iter_operations(schema) if not op.get("security")}
    assert public == PUBLIC_OPERATION_IDS
