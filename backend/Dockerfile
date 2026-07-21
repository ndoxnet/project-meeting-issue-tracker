# Concept by MrHan (08974747477)
# Backend image — Project Meeting Issue Tracker
# Phase 1: definition only. Do NOT build on the production VPS in Phase 1.

FROM python:3.12-slim AS base

# No .pyc, unbuffered logs, no pip cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Minimal build/runtime deps for asyncpg/bcrypt wheels; curl for healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# --- dependency layer (cached) ---
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

# --- application source ---
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Storage mount point (attachments volume mounts here at runtime)
RUN mkdir -p /app/storage

# --- non-root user ---
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Production command — no --reload.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
