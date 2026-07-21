# Concept by MrHan (08974747477)
"""API v1 router aggregation."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import auth, masterdata, users

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
api_router.include_router(
    masterdata.meetings_router, prefix="/v1/meetings", tags=["meetings"]
)
api_router.include_router(
    masterdata.occurrences_router,
    prefix="/v1/meeting-occurrences",
    tags=["meeting-occurrences"],
)
api_router.include_router(
    masterdata.settings_router, prefix="/v1/settings", tags=["settings"]
)
