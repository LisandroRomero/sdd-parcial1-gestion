from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.router import router as api_v1_router
from backend.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate settings on startup (fail fast on missing required env vars).
    get_settings()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
