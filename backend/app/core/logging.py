"""
Structured JSON logging for Adhi Compliance.

Usage:
    from app.core.logging import configure_logging, get_logger, RequestLoggingMiddleware

    # In main.py startup:
    configure_logging(log_level=settings.LOG_LEVEL.value)
    app.add_middleware(RequestLoggingMiddleware)

    # In any module:
    logger = get_logger(__name__)
    logger.info("my_event", extra={"key": "value"})
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from pythonjsonlogger import jsonlogger
    _JSON_AVAILABLE = True
except ImportError:
    _JSON_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configure root logger
# ---------------------------------------------------------------------------

def configure_logging(log_level: str = "INFO") -> None:
    """
    Set up the root logger with a JSON formatter (falls back to plain text
    if python-json-logger is not installed).

    Call once at application startup before any other logging occurs.
    """
    handler = logging.StreamHandler()

    if _JSON_AVAILABLE:
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Silence noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for use in modules."""
    return logging.getLogger(name)


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that logs every inbound HTTP request with:
      - request_id  (UUID, also injected into the response header X-Request-ID)
      - method, path, client IP
      - response status code
      - duration in ms
    """

    def __init__(self, app, logger: logging.Logger | None = None) -> None:
        super().__init__(app)
        self._logger = logger or logging.getLogger("adhi.requests")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        self._logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        self._logger.info(
            "request_finished",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
