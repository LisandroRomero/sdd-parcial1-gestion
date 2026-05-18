from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Compute env_file relative to this file (core/config.py → backend/.env)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BACKEND_DIR, ".env")


class Settings(BaseSettings):
    """Application settings loaded from env (optionally via backend/.env).

    This module is intentionally small and typed. It is used by the app entrypoint
    to fail fast on missing required configuration.
    """

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Food Store API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Required for DB operations.
    database_url: str = Field(alias="DATABASE_URL")

    # JWT configuration.
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
    )

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        alias="CORS_ORIGINS",
    )

    # MercadoPago placeholders.
    mercadopago_access_token: str = Field(alias="MERCADOPAGO_ACCESS_TOKEN")
    mercadopago_webhook_secret: str = Field(
        default="",
        alias="MERCADOPAGO_WEBHOOK_SECRET",
    )
    mercadopago_public_key: str = Field(
        default="",
        alias="MP_PUBLIC_KEY",
    )
    mercadopago_notification_url: str = Field(
        default="",
        alias="MP_NOTIFICATION_URL",
    )

    sanitize_inputs: bool = Field(default=False, alias="SANITIZE_INPUTS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
