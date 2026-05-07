from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.exceptions import AppException


# ------------------------------------------------------------------
# Exception handler (registered via app.add_exception_handler)
# ------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers that map ``AppException`` subclasses
    to structured JSON error responses.

    Call during app creation in ``main.py``.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


# ------------------------------------------------------------------
# Request ID middleware (registered via app.add_middleware)
# ------------------------------------------------------------------


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique ``X-Request-ID`` to every request.

    If the client provides an ``X-Request-ID`` header, it is echoed
    back unchanged. Otherwise, a new UUID v4 is generated.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
