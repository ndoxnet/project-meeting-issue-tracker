# Concept by MrHan (08974747477)
from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Standard error envelope: {"error": {code, message, request_id}}."""

    error: ErrorBody


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=200)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)


class Page[T](BaseModel):
    items: list[T]
    meta: PageMeta


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
