from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from env (optionally via backend/.env).

    This module is intentionally small and typed. It is used by the app entrypoint
    to fail fast on missing required configuration.
    """

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Food Store API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Required for DB operations.
    database_url: str = Field(alias="DATABASE_URL")

    # JWT placeholders (real wiring lives in auth feature).
    secret_key: str = Field(alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
