import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError as DomainValidationError,
    ConflictError,
)

logger = logging.getLogger("adhi_compliance")


def _error_response(status_code: int, error: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "detail": detail,
            "status_code": status_code,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI application."""

    # ------------------------------------------------------------------
    # Custom domain exceptions → structured HTTP responses
    # ------------------------------------------------------------------

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return _error_response(404, "Not Found", str(exc))

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return _error_response(401, "Unauthorized", exc.message)

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return _error_response(403, "Forbidden", exc.message)

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(request: Request, exc: DomainValidationError):
        return _error_response(422, "Validation Error", str(exc))

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return _error_response(409, "Conflict", exc.message)

    # ------------------------------------------------------------------
    # Standard FastAPI / Starlette exceptions
    # ------------------------------------------------------------------

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP %s on %s %s — %s",
            exc.status_code, request.method, request.url.path, exc.detail
        )
        return _error_response(
            status_code=exc.status_code,
            error=_status_label(exc.status_code),
            detail=str(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        detail = "; ".join(
            f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in errors
        )
        logger.warning("Validation error on %s %s — %s", request.method, request.url.path, detail)
        return _error_response(
            status_code=422,
            error="Unprocessable Entity",
            detail=detail,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception on %s %s", request.method, request.url.path
        )
        return _error_response(
            status_code=500,
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again or contact support.",
        )


def _status_label(status_code: int) -> str:
    labels = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }
    return labels.get(status_code, "Error")
