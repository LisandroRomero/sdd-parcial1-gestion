from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, create_engine

from backend.core.config import get_settings


def _build_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = _build_engine()


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a per-request DB session."""

    with Session(engine) as session:
        yield session
