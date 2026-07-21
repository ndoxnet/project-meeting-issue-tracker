# Concept by MrHan (08974747477)
"""Application configuration via Pydantic Settings.

Values are read from the environment (see .env.example). No secret has a
production-usable default; DEBUG defaults to False.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "Project Meeting Issue Tracker"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ---- Auth / security ----
    SECRET_KEY: str = Field(default="CHANGE_ME", min_length=8)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://issue_tracker_app:CHANGE_ME@postgres:5432/issue_tracker"

    # ---- CORS ----
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5200"

    # ---- Localization / business rules ----
    DISPLAY_TIMEZONE: str = "Asia/Jakarta"
    STAGNANT_DAYS: int = 7
    ISSUE_CODE_PREFIX: str = "ISS"

    # ---- Attachments ----
    ATTACHMENT_MAX_MB: int = 10
    ATTACHMENT_ALLOWED_TYPES: str = "application/pdf,image/jpeg,image/png"
    STORAGE_PATH: str = "/app/storage"

    # ---- Initial admin (seed only; not a runtime credential) ----
    ADMIN_EMAIL: str = "CHANGE_ME"
    ADMIN_USERNAME: str = "CHANGE_ME"
    ADMIN_INITIAL_PASSWORD: str = "CHANGE_ME"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def attachment_allowed_types_list(self) -> list[str]:
        return [t.strip() for t in self.ATTACHMENT_ALLOWED_TYPES.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Import this, do not instantiate Settings directly."""
    return Settings()
