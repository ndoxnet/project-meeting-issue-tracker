# Concept by MrHan (08974747477)
"""FastAPI application entrypoint.

Phase 2A: auth, users, and master data are wired. The database engine is created
lazily (first request), never at import time. Attachments/issue business logic
arrive in Phase 2B.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.db.session import dispose_engine
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: nothing eager — the engine is created on first DB use.
    yield
    # Shutdown: dispose the async engine if it was created.
    await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Order matters: request-id first so handlers/logs can see it.
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness endpoint. Does not touch the database."""
    return {
        "status": "ok",
        "service": "project-meeting-issue-tracker-api",
        "version": settings.APP_VERSION,
    }


app.include_router(api_router, prefix="/api")
