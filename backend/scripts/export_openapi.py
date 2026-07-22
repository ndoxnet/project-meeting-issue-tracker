# Concept by MrHan (08974747477)
"""Export the FastAPI OpenAPI schema to docs/api/openapi.{json,yaml}.

Deterministic, no database, no secrets. Sets a fixed SECRET_KEY only to satisfy
settings validation at import (never written out). Run via `make openapi-export`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure settings validation passes without a real environment. This value is
# used ONLY to import the app for schema generation; it is never emitted.
os.environ.setdefault("SECRET_KEY", "openapi-export-placeholder-key-000000000000")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")

# docs/api at the repository root (two levels up from backend/).
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "api"


def build_schema() -> dict:
    from app.main import app  # imported here so env is set first

    schema = app.openapi()
    if "openapi" not in schema or "paths" not in schema:
        raise SystemExit("Generated schema is invalid (missing openapi/paths).")
    return schema


def write_json(schema: dict) -> Path:
    path = OUT_DIR / "openapi.json"
    # Stable formatting: sorted keys, 2-space indent, trailing newline.
    path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_yaml(schema: dict) -> Path | None:
    try:
        import yaml
    except ModuleNotFoundError:
        print("[export_openapi] PyYAML not installed — skipping YAML (JSON is canonical).")
        return None
    path = OUT_DIR / "openapi.yaml"
    path.write_text(
        yaml.safe_dump(schema, sort_keys=True, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    return path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    schema = build_schema()
    j = write_json(schema)
    y = write_yaml(schema)
    n_paths = len(schema.get("paths", {}))
    n_ops = sum(
        1
        for methods in schema.get("paths", {}).values()
        for m in methods
        if m in {"get", "post", "put", "patch", "delete"}
    )
    n_schemas = len(schema.get("components", {}).get("schemas", {}))
    print(
        f"[export_openapi] OpenAPI {schema['openapi']} v{schema['info']['version']}: "
        f"{n_paths} paths, {n_ops} operations, {n_schemas} schemas"
    )
    print(f"[export_openapi] wrote {j.relative_to(REPO_ROOT)}")
    if y:
        print(f"[export_openapi] wrote {y.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
