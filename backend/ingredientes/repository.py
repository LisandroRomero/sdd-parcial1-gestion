from __future__ import annotations

from typing import Optional

from sqlalchemy import delete
from sqlmodel import Session, select

from backend.ingredientes.model import Ingrediente, ProductoIngrediente
from backend.core.patterns import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repository for Ingrediente — extends BaseRepository with ingredient-specific queries."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_active(
        self,
        *,
        es_alergeno: Optional[bool],
        skip: int,
        limit: int,
        include_deleted: bool = False,
    ) -> tuple[list[Ingrediente], int]:
        """Return a paginated list of active (non-deleted) ingredientes.

        Optionally filtered by ``es_alergeno``.

        Args:
            es_alergeno: If provided, filter by this boolean value.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            include_deleted: If True, include soft-deleted items.

        Returns:
            A tuple of (items, total) where total is the count before pagination.
        """
        stmt = select(Ingrediente)
        if not include_deleted:
            stmt = stmt.where(Ingrediente.deleted_at.is_(None))
        if es_alergeno is not None:
            stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)

        all_items = self.session.exec(stmt).all()
        total = len(all_items)
        items = self.session.exec(stmt.offset(skip).limit(limit)).all()
        return list(items), total

    def get_by_id_active(self, id: int) -> Optional[Ingrediente]:
        """Return an active (non-deleted) ingrediente by id, or None.

        Args:
            id: Primary key of the ingrediente.

        Returns:
            The Ingrediente if found and not soft-deleted, otherwise None.
        """
        stmt = select(Ingrediente).where(
            Ingrediente.id == id,
            Ingrediente.deleted_at.is_(None),
        )
        return self.session.exec(stmt).first()

    def exists_by_nombre(
        self,
        nombre: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Return True if an active ingrediente with the given nombre exists.

        Args:
            nombre: The name to check for uniqueness.
            exclude_id: If provided, exclude this ID from the check (useful for updates).

        Returns:
            True if a conflicting active ingrediente exists, False otherwise.
        """
        stmt = select(Ingrediente).where(
            Ingrediente.nombre == nombre,
            Ingrediente.deleted_at.is_(None),
        )
        if exclude_id is not None:
            stmt = stmt.where(Ingrediente.id != exclude_id)
        return self.session.exec(stmt).first() is not None

    def agregar_a_producto(
        self,
        producto_id: int,
        ingrediente_id: int,
        cantidad: Optional[float],
        unidad: Optional[str],
    ) -> ProductoIngrediente:
        asociacion = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            cantidad=cantidad,
            unidad=unidad,
        )
        self.session.add(asociacion)
        self.session.flush()
        self.session.refresh(asociacion)
        return asociacion

    def existe_asociacion(self, producto_id: int, ingrediente_id: int) -> bool:
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id,
        )
        return self.session.exec(stmt).first() is not None

    def listar_por_producto(
        self, producto_id: int
    ) -> list[tuple[ProductoIngrediente, Ingrediente]]:
        stmt = (
            select(ProductoIngrediente, Ingrediente)
            .join(Ingrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
            .where(
                ProductoIngrediente.producto_id == producto_id,
                Ingrediente.deleted_at.is_(None),
            )
        )
        return list(self.session.exec(stmt).all())

    def remover_de_producto(self, producto_id: int, ingrediente_id: int) -> bool:
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id,
        )
        asociacion = self.session.exec(stmt).first()
        if asociacion is None:
            return False
        self.session.exec(
            delete(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id,
                ProductoIngrediente.ingrediente_id == ingrediente_id,
            )
        )
        self.session.flush()
        return True
