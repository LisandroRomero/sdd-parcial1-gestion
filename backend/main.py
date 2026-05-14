from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import backend.core.models  # noqa: F401 — registers all SQLModel mappers
from backend.api.v1.router import router as api_v1_router
from backend.core.config import get_settings
from backend.core.middleware import (
    InputSanitizationMiddleware,
    RequestIDMiddleware,
    register_exception_handlers,
)
from backend.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate settings on startup (fail fast on missing required env vars,
    # including JWT_SECRET_KEY and REFRESH_TOKEN_EXPIRE_DAYS).
    get_settings()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # ── Rate limiter ───────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Middleware ──────────────────────────────────────────────
    # Order matters: RequestID should run early so all downstream
    # code (including error responses) gets the ID.

    app.add_middleware(RequestIDMiddleware)
    if settings.sanitize_inputs:
        app.add_middleware(InputSanitizationMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ─────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
