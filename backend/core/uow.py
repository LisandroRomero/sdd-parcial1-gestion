from __future__ import annotations

from collections.abc import Callable

from sqlmodel import Session


class UnitOfWork:
    """Minimal Unit of Work.

    Pattern:

    ```py
    def some_service(uow_factory: Callable[[], UnitOfWork]):
        with uow_factory() as uow:
            ... # do work using uow.session
            uow.commit()
    ```

    If an exception is raised inside the context manager, it rolls back.
    """

    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.session is not None

        if exc_type is not None:
            self.session.rollback()

        self.session.close()

    def commit(self) -> None:
        assert self.session is not None
        self.session.commit()
