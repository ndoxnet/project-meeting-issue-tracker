# Concept by MrHan (08974747477)
"""Domain exceptions and consistent error responses.

All errors are serialized as:
    {"error": {"code": "...", "message": "...", "request_id": "..."}}
Tracebacks are never sent to the client. In development the traceback is logged
(with secrets redacted) but not returned.
"""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base application error with a stable machine code and HTTP status."""

    code = "INTERNAL_ERROR"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message


class AuthenticationError(AppError):
    code = "AUTHENTICATION_FAILED"
    http_status = status.HTTP_401_UNAUTHORIZED
    message = "Invalid credentials"


class AuthorizationError(AppError):
    code = "AUTHORIZATION_FAILED"
    http_status = status.HTTP_403_FORBIDDEN
    message = "Insufficient permissions"


class NotFoundError(AppError):
    code = "NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class ConflictError(AppError):
    code = "CONFLICT"
    http_status = status.HTTP_409_CONFLICT
    message = "Resource conflict"


class DomainValidationError(AppError):
    code = "VALIDATION_ERROR"
    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "Validation failed"


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _error_response(
    *, code: str, message: str, http_status: int, request_id: str | None
) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(
            code=exc.code,
            message=exc.message,
            http_status=exc.http_status,
            request_id=_request_id(request),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request_id=_request_id(request),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {
            401: "AUTHENTICATION_FAILED",
            403: "AUTHORIZATION_FAILED",
            404: "NOT_FOUND",
            409: "CONFLICT",
        }.get(exc.status_code, "HTTP_ERROR")
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return _error_response(
            code=code,
            message=message,
            http_status=exc.status_code,
            request_id=_request_id(request),
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
        # Do not leak internals. (Structured logging of the category happens in
        # middleware/logging; secrets are redacted there.)
        return _error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=_request_id(request),
        )
