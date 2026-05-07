from __future__ import annotations

from typing import Generic, TypeVar

from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Generic repository providing standard CRUD operations.

    Usage:
        class UsuarioRepository(BaseRepository[Usuario]):
            pass

        repo = UsuarioRepository(session)
        usuario = repo.get(1)

    Soft-delete: if the model class defines a ``deleted_at`` column,
    all read operations automatically filter out soft-deleted records.
    Pass ``include_deleted=True`` to override.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self._model: type[T] | None = None

    @property
    def model(self) -> type[T]:
        if self._model is None:
            # Resolve the concrete model from generic type arguments.
            # Each subclass sets __model_type__ via __init_subclass__.
            self._model = self.__class__.__model_type__
        return self._model

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # Walk the MRO to find the first concrete Generic type arg.
        for base in cls.__orig_bases__:  # type: ignore[attr-defined]
            args = getattr(base, "__args__", ())
            if args:
                cls.__model_type__ = args[0]
                return
        # Fallback: mark as abstract (no concrete model yet).
        cls.__model_type__ = None  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Soft-delete helpers
    # ------------------------------------------------------------------

    @property
    def _soft_delete_enabled(self) -> bool:
        return hasattr(self.model, "deleted_at")

    def _active_filter(self, include_deleted: bool = False):
        """Return a WHERE clause that excludes soft-deleted rows."""
        if not self._soft_delete_enabled or include_deleted:
            return True
        return self.model.deleted_at.is_(None)  # type: ignore[union-attr]

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def add(self, entity: T) -> T:
        """Add a new entity to the session (pending commit via UoW)."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def get(self, id: object) -> T | None:
        """Retrieve an entity by primary key, or None if not found."""
        return self.session.get(self.model, id)

    def get_by(self, include_deleted: bool = False, **filters: object) -> T | None:
        """Retrieve the first entity matching the given column-value pairs."""
        stmt = select(self.model).where(
            *(
                getattr(self.model, col) == val
                for col, val in filters.items()
            ),
            self._active_filter(include_deleted),
        )
        return self.session.exec(stmt).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[T]:
        """Return a paginated list of entities."""
        stmt = (
            select(self.model)
            .where(self._active_filter(include_deleted))
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def update(self, entity: T) -> T:
        """Merge changes to an existing entity into the session."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity.

        If the model supports soft-delete, sets ``deleted_at`` instead
        of removing the row.
        """
        if self._soft_delete_enabled:
            from datetime import datetime, timezone

            entity.deleted_at = datetime.now(timezone.utc)  # type: ignore[union-attr]
            self.session.add(entity)
        else:
            self.session.delete(entity)
        self.session.flush()

    def exists(self, **filters: object) -> bool:
        """Return True if at least one entity matches the given filters."""
        stmt = select(self.model).where(
            *(
                getattr(self.model, col) == val
                for col, val in filters.items()
            ),
        )
        return self.session.exec(stmt).first() is not None
