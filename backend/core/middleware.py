from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.exceptions import AppException


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return request_id
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


def _format_validation_errors(raw_errors: list[dict]) -> list[dict]:
    formatted: list[dict] = []
    for error in raw_errors:
        loc = error.get("loc", [])
        field = "unknown"
        if isinstance(loc, (list, tuple)):
            parts = [
                str(part)
                for part in loc
                if part not in ("body", "query", "path", "header", "cookie")
            ]
            if parts:
                field = ".".join(parts)
            elif loc:
                field = str(loc[-1])
        else:
            field = str(loc)

        formatted.append(
            {
                "field": field,
                "message": str(error.get("msg", "Error de validación")),
                "code": str(error.get("type", "validation_error")),
            }
        )
    return formatted


def _build_problem_detail(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    code: str | None = None,
    errors: list[dict] | None = None,
) -> dict:
    payload: dict = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
        "requestId": _get_request_id(request),
        "timestamp": _utc_timestamp(),
    }

    if code:
        payload["code"] = code

    if errors:
        payload["errors"] = errors

    return payload


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        status_code = exc.status_code
        title = status.HTTP_STATUS_CODES.get(status_code, "Error")
        payload = _build_problem_detail(
            request=request,
            status_code=status_code,
            title=title,
            detail=exc.detail,
            code=exc.code,
        )
    elif isinstance(exc, (RequestValidationError, ValidationError)):
        errors = _format_validation_errors(exc.errors())
        payload = _build_problem_detail(
            request=request,
            status_code=422,
            title="Validation Error",
            detail="Error de validación en los datos enviados",
            errors=errors,
        )
        status_code = 422
    else:
        import traceback
        print(f"UNHANDLED EXCEPTION: {repr(exc)}", flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        payload = _build_problem_detail(
            request=request,
            status_code=500,
            title="Internal Server Error",
            detail="Internal server error",
        )
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )


# ------------------------------------------------------------------
# Exception handler (registered via app.add_exception_handler)
# ------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers that map ``AppException`` subclasses
    to structured JSON error responses.

    Call during app creation in ``main.py``.
    """

    app.add_exception_handler(AppException, global_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    app.add_exception_handler(ValidationError, global_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)


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
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ------------------------------------------------------------------
# Input sanitization middleware (optional, configurable)
# ------------------------------------------------------------------


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    _html_pattern = re.compile(r"<[^>]*>")
    _sqli_patterns = (
        re.compile(r"(?i)\b(select|insert|update|delete|drop|union|alter|create|truncate)\b"),
        re.compile(r"(?i)\b(or|and)\b\s+\d+=\d+"),
        re.compile(r"(?i)--"),
        re.compile(r"(?i)/\*|\*/"),
        re.compile(r"(?i)\b(or|and)\b\s+['\"]?.+['\"]?=\s*['\"]?.+['\"]?"),
    )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> JSONResponse:
        for _, value in request.query_params.multi_items():
            if self._has_sqli(value):
                return self._sanitization_error(request)

        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    payload = json.loads(body_bytes)
                except json.JSONDecodeError:
                    payload = None

                if payload is not None:
                    sanitized_payload, has_sqli = self._sanitize_value(payload)
                    if has_sqli:
                        return self._sanitization_error(request)

                    if sanitized_payload != payload:
                        new_body = json.dumps(sanitized_payload).encode("utf-8")

                        async def receive() -> dict:
                            return {"type": "http.request", "body": new_body, "more_body": False}

                        request._receive = receive  # type: ignore[attr-defined]

        response = await call_next(request)
        return response

    def _sanitize_value(self, value: object) -> tuple[object, bool]:
        if isinstance(value, str):
            if self._has_sqli(value):
                return value, True
            sanitized = self._html_pattern.sub("", value)
            return sanitized, False

        if isinstance(value, list):
            sanitized_items = []
            has_sqli = False
            for item in value:
                sanitized_item, item_has_sqli = self._sanitize_value(item)
                has_sqli = has_sqli or item_has_sqli
                sanitized_items.append(sanitized_item)
            return sanitized_items, has_sqli

        if isinstance(value, dict):
            sanitized_dict: dict = {}
            has_sqli = False
            for key, item in value.items():
                sanitized_item, item_has_sqli = self._sanitize_value(item)
                has_sqli = has_sqli or item_has_sqli
                sanitized_dict[key] = sanitized_item
            return sanitized_dict, has_sqli

        return value, False

    def _has_sqli(self, value: str) -> bool:
        return any(pattern.search(value) for pattern in self._sqli_patterns)

    def _sanitization_error(self, request: Request) -> JSONResponse:
        payload = _build_problem_detail(
            request=request,
            status_code=400,
            title=status.HTTP_STATUS_CODES.get(400, "Bad Request"),
            detail="Input sanitization failed",
            code="INPUT_SANITIZATION",
        )
        return JSONResponse(
            status_code=400,
            content=payload,
            media_type="application/problem+json",
        )
