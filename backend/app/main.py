# Concept by MrHan (08974747477)
"""FastAPI application entrypoint.

Phase 1 skeleton: exposes /health and a placeholder API router. No database
connection is opened at import time or during startup in this phase.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Minimal lifecycle hook.

    Phase 1: no DB engine, pool, or migration is started here. Phase 2 will
    initialize the async engine and perform readiness checks.
    """
    # startup (intentionally empty in Phase 1)
    yield
    # shutdown (intentionally empty in Phase 1)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness endpoint. Does not touch the database."""
    return {
        "status": "ok",
        "service": "project-meeting-issue-tracker-api",
        "version": settings.APP_VERSION,
    }


app.include_router(api_router, prefix="/api")
