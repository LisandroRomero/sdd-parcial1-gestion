from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlmodel import Session

if TYPE_CHECKING:
    from backend.core.patterns import BaseRepository


class _ReposRegistry:
    """Lazily-initialized repository registry.

    Repositories are created on first access and cached for the
    lifetime of the owning UnitOfWork. All repositories share the
    same session, ensuring atomic transactions across multiple repos.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._factories: dict[str, Callable[[Session], BaseRepository]] = {}
        self._instances: dict[str, BaseRepository] = {}

    def register(
        self,
        name: str,
        factory: Callable[[Session], BaseRepository],
    ) -> None:
        """Register a repository factory.

        Args:
            name: Attribute name used for access (e.g. ``"usuarios"``).
            factory: Callable that receives a ``Session`` and returns a
                ``BaseRepository`` instance.
        """
        self._factories[name] = factory
        # Clear cached instance so the next access picks up the new factory.
        self._instances.pop(name, None)

    def __getattr__(self, name: str) -> BaseRepository:
        if name.startswith("_"):
            raise AttributeError(name)
        # Check cache first.
        if name in self._instances:
            return self._instances[name]
        # Lazily create from factory.
        factory = self._factories.get(name)
        if factory is None:
            raise AttributeError(
                f"Repository '{name}' is not registered. "
                f"Use uow.repos.register('{name}', factory) first."
            )
        instance = factory(self._session)
        self._instances[name] = instance
        return instance


class UnitOfWork:
    """Unit of Work with commit/rollback and integrated repository access.

    Pattern::

        with uow_factory() as uow:
            uow.repos.usuarios.add(new_user)
            uow.commit()

    All repositories accessed via ``uow.repos`` share the same database
    session. On success, call ``commit()`` explicitly. On exception,
    the context manager automatically rolls back.
    """

    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self.session: Session | None = None
        self._repos: _ReposRegistry | None = None

    @property
    def repos(self) -> _ReposRegistry:
        """Access the lazily-initialized repository registry."""
        assert self.session is not None, (
            "Cannot access repos outside a UoW context. "
            "Use 'with uow_factory() as uow:' first."
        )
        if self._repos is None:
            self._repos = _ReposRegistry(self.session)
        return self._repos

    def __enter__(self) -> UnitOfWork:
        self.session = self._session_factory()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        assert self.session is not None

        # HTTPException = intentional business response (401, 403, 409, …).
        # Any writes made before raising are intentional and must be committed
        # (e.g. revoking all tokens on replay-attack detection before 401).
        # Unexpected exceptions (DB errors, assertion failures, etc.) roll back.
        if exc_type is not None:
            if isinstance(exc_type, type) and issubclass(exc_type, HTTPException):
                self.session.commit()
            else:
                self.session.rollback()

        self.session.close()

    def commit(self) -> None:
        """Commit all pending changes to the database."""
        assert self.session is not None
        self.session.commit()
