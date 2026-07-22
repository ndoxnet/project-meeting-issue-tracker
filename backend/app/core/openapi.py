# Concept by MrHan (08974747477)
"""OpenAPI metadata: canonical tags (with descriptions) and a security scheme.

Kept separate from main.py so the export script and contract tests can import the
tag/description constants without pulling request-handling concerns."""

from __future__ import annotations

API_DESCRIPTION = """\
Internal API for the **Project Meeting Issue Tracker** (Project Control team).

The **Issue** is the primary entity; meetings only add follow-up updates. This is
the frozen **v1** contract (base path `/api/v1`) used by the Phase 2C frontend.

Auth: Bearer JWT (HS256). Authorization uses the user's *current database role*,
not just the token claim. Timestamps are UTC; date-only fields are `YYYY-MM-DD`
and displayed in Asia/Jakarta by clients.
"""

# Canonical, ordered tags. Every operation is assigned exactly one of these.
OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": "Health", "description": "Liveness/readiness. Public, no auth, no DB."},
    {
        "name": "Authentication",
        "description": "Login, logout (client discards token), current user.",
    },
    {"name": "Users", "description": "User & role management. Admin only."},
    {
        "name": "Categories",
        "description": "Issue category master data. Read: any role; write: Admin.",
    },
    {
        "name": "Responsible Parties",
        "description": "Responsible-party master data. Read: any; write: Admin.",
    },
    {"name": "Meetings", "description": "Meeting-type master data. Read: any; write: Admin."},
    {
        "name": "Meeting Occurrences",
        "description": "Single meeting instances. Read: any; create/update: Editor+.",
    },
    {
        "name": "Issues",
        "description": "Issue register + lifecycle (create/list/detail/status/close/reopen).",
    },
    {"name": "Issue Updates", "description": "Append-only follow-up history and Admin void."},
    {"name": "Attachments", "description": "Secure per-issue file upload/download/soft-remove."},
    {
        "name": "Dashboard",
        "description": "Monitoring aggregates (overdue, stagnant, trends). Any role.",
    },
    {"name": "Reports", "description": "Filtered CSV export of the issue register. Any role."},
    {"name": "Settings", "description": "Application settings. Read: any; write: Admin."},
]

CONTACT = {"name": "MrHan (Project Control)", "email": "project-control@example.com"}
LICENSE = {"name": "Proprietary — internal use only"}

# Development servers only — no production host or secret.
SERVERS = [
    {"url": "http://127.0.0.1:5200", "description": "Local (frontend proxy to backend)"},
    {"url": "http://localhost:8000", "description": "Local backend (direct)"},
]


def build_openapi(app) -> dict:
    """Custom OpenAPI: base schema + the standard error envelope models injected
    into components (they are the documented shape of every 4xx/5xx response but
    are not tied to a single endpoint's response_model)."""
    from fastapi.openapi.utils import get_openapi

    from app.schemas.common import ErrorBody, ErrorResponse

    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
        contact=CONTACT,
        license_info=LICENSE,
        servers=SERVERS,
    )
    components = schema.setdefault("components", {}).setdefault("schemas", {})
    # Pydantic v2 refs use #/components/schemas/<Name>; models here are flat.
    for model in (ErrorBody, ErrorResponse):
        components[model.__name__] = model.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    app.openapi_schema = schema
    return schema
