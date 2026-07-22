# Concept by MrHan (08974747477)
"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    attachments,
    auth,
    dashboard,
    issue_updates,
    issues,
    masterdata,
    reports,
    users,
)

api_router = APIRouter()


@api_router.get("/ping", tags=["meta"])
async def ping() -> dict[str, str]:
    """Trivial connectivity check under the API prefix (no DB access)."""
    return {"message": "pong"}


api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(
    masterdata.categories_router, prefix="/v1/categories", tags=["categories"]
)
api_router.include_router(
    masterdata.responsible_parties_router,
    prefix="/v1/responsible-parties",
    tags=["responsible-parties"],
)
api_router.include_router(masterdata.meetings_router, prefix="/v1/meetings", tags=["meetings"])
api_router.include_router(
    masterdata.occurrences_router,
    prefix="/v1/meeting-occurrences",
    tags=["meeting-occurrences"],
)
api_router.include_router(masterdata.settings_router, prefix="/v1/settings", tags=["settings"])
# Issue endpoints. issue_updates & attachments share the /v1/issues prefix
# (their paths are /{issue_id}/updates and /{issue_id}/attachments).
api_router.include_router(issues.router, prefix="/v1/issues", tags=["issues"])
api_router.include_router(issue_updates.router, prefix="/v1/issues", tags=["issue-updates"])
api_router.include_router(attachments.router, prefix="/v1/issues", tags=["attachments"])
api_router.include_router(dashboard.router, prefix="/v1/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
