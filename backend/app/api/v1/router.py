# Concept by MrHan (08974747477)
"""API v1 router aggregation.

Phase 1: a placeholder router only. Endpoint modules (auth, issues, meetings,
dashboard, master data, audit) are wired in Phase 2.
"""
from __future__ import annotations

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/ping", tags=["meta"])
async def ping() -> dict[str, str]:
    """Trivial connectivity check under the API prefix (no DB access)."""
    return {"message": "pong"}


# Phase 2 will include the real routers, e.g.:
# from app.api.v1.endpoints import auth, issues, meetings, dashboard
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
