# Concept by MrHan (08974747477)
"""Application configuration via Pydantic Settings.

Strictly validated. No secret has a production-usable default. Values are read
from the environment (see .env.example). Secret values are never logged.
"""

from __future__ import annotations

from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACEHOLDER = "CHANGE_ME"


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
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    # ---- Auth / security ----
    SECRET_KEY: str = PLACEHOLDER
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480, ge=1, le=7 * 24 * 60)

    # ---- Database ----
    DATABASE_URL: str = (
        "postgresql+asyncpg://issue_tracker_app:CHANGE_ME@postgres:5432/issue_tracker"
    )

    # ---- CORS ----
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5200"

    # ---- Localization / business rules ----
    DISPLAY_TIMEZONE: str = "Asia/Jakarta"
    STAGNANT_DAYS: int = Field(default=7, ge=1, le=365)
    ISSUE_CODE_PREFIX: str = "ISS"

    # ---- Attachments ----
    ATTACHMENT_MAX_MB: int = Field(default=10, ge=1, le=1024)
    ATTACHMENT_ALLOWED_TYPES: str = "application/pdf,image/jpeg,image/png"
    STORAGE_PATH: str = "/app/storage"

    # ---- Initial admin (seed only; not a runtime credential) ----
    ADMIN_EMAIL: str = PLACEHOLDER
    ADMIN_USERNAME: str = PLACEHOLDER
    ADMIN_INITIAL_PASSWORD: str = PLACEHOLDER

    # ---- validators ----
    @field_validator("APP_ENV")
    @classmethod
    def _normalize_env(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def _check_alg(cls, v: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}
        if v not in allowed:
            raise ValueError(f"JWT_ALGORITHM must be one of {sorted(allowed)}")
        return v

    @field_validator("DISPLAY_TIMEZONE")
    @classmethod
    def _check_tz(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError as exc:  # pragma: no cover - env dependent
            raise ValueError(f"DISPLAY_TIMEZONE '{v}' is not a valid IANA timezone") from exc
        return v

    @model_validator(mode="after")
    def _validate_secret_and_env(self) -> Settings:
        # SECRET_KEY must be set and reasonably strong.
        if self.SECRET_KEY == PLACEHOLDER or len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be set to a strong value (>= 32 chars); "
                "generate with `openssl rand -hex 32`."
            )
        # DEBUG must not be enabled in production.
        if self.is_production and self.DEBUG:
            raise ValueError("DEBUG must be false when APP_ENV=production")
        return self

    # ---- derived ----
    @property
    def is_production(self) -> bool:
        return self.APP_ENV in {"production", "prod"}

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def attachment_allowed_types_list(self) -> list[str]:
        return [t.strip() for t in self.ATTACHMENT_ALLOWED_TYPES.split(",") if t.strip()]

    @property
    def display_tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.DISPLAY_TIMEZONE)


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Import this; do not instantiate Settings directly.

    Tests may override by clearing the cache: ``get_settings.cache_clear()``.
    """
    return Settings()
