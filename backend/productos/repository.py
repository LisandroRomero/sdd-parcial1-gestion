from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, exists, func, or_
from sqlmodel import Session, select

from backend.core.patterns import BaseRepository
from backend.categorias.model import Categoria
from backend.ingredientes.model import Ingrediente, ProductoIngrediente
from backend.productos.model import Producto, ProductoCategoria
from backend.productos.schemas import ProductoFiltros


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id_active_with_lock(self, id: int) -> Optional[Producto]:
        """Return an active Producto by PK with a SELECT FOR UPDATE row lock.

        Use during order creation to prevent concurrent stock decrements
        from racing with each other.
        """
        stmt = (
            select(Producto)
            .where(Producto.id == id, Producto.deleted_at.is_(None))
            .with_for_update()
        )
        return self.session.exec(stmt).first()

    def get_by_id_active(self, id: int) -> Optional[Producto]:
        stmt = select(Producto).where(
            Producto.id == id,
            Producto.deleted_at.is_(None),
        )
        return self.session.exec(stmt).first()

    def exists_by_sku(self, sku: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(Producto).where(
            Producto.codigo_sku == sku,
            Producto.deleted_at.is_(None),
        )
        if exclude_id is not None:
            stmt = stmt.where(Producto.id != exclude_id)
        return self.session.exec(stmt).first() is not None

    def sync_categorias(self, producto_id: int, categoria_ids: list[int]) -> None:
        # Replace all pivots by spec (DELETE + INSERT).
        self.session.exec(
            delete(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
        )

        for categoria_id in categoria_ids:
            self.session.add(
                ProductoCategoria(
                    producto_id=producto_id,
                    categoria_id=categoria_id,
                    es_principal=False,
                )
            )

        self.session.flush()

    def get_categoria_ids_activos(self, categoria_ids: list[int]) -> list[int]:
        if not categoria_ids:
            return []

        stmt = select(Categoria.id).where(
            Categoria.id.in_(categoria_ids),
            Categoria.deleted_at.is_(None),
        )
        return list(self.session.exec(stmt).all())

    def list_public(self, filtros: ProductoFiltros, include_deleted: bool = False) -> tuple[list[Producto], int]:
        """Return paginated public products filtered by ProductoFiltros.

        Base filter: deleted_at IS NULL (unless include_deleted=True) and disponible = True (unless filtros.disponible is set).
        Returns (paginated_items, total_count).
        """
        stmt = select(Producto)
        if not include_deleted:
            stmt = stmt.where(Producto.deleted_at.is_(None))

        # Apply disponible filter — default to True when not specified
        if filtros.disponible is None:
            stmt = stmt.where(Producto.disponible.is_(True))
        else:
            stmt = stmt.where(Producto.disponible == filtros.disponible)

        # Optional: categoria_id filter via JOIN to producto_categorias
        if filtros.categoria_id is not None:
            stmt = stmt.join(
                ProductoCategoria,
                ProductoCategoria.producto_id == Producto.id,
            ).where(ProductoCategoria.categoria_id == filtros.categoria_id)

        # Optional: price range filters
        if filtros.precio_min is not None:
            stmt = stmt.where(Producto.precio_base >= filtros.precio_min)
        if filtros.precio_max is not None:
            stmt = stmt.where(Producto.precio_base <= filtros.precio_max)

        # Optional: text search (case-insensitive) on nombre and descripcion
        if filtros.busqueda is not None:
            v = filtros.busqueda
            stmt = stmt.where(
                or_(
                    Producto.nombre.ilike(f"%{v}%"),
                    Producto.descripcion.ilike(f"%{v}%"),
                )
            )

        # Optional: alergenos EXISTS subquery
        if filtros.tiene_alergenos is not None:
            alergeno_exists = exists(
                select(ProductoIngrediente.producto_id)
                .join(Ingrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
                .where(
                    ProductoIngrediente.producto_id == Producto.id,
                    Ingrediente.es_alergeno.is_(True),
                    Ingrediente.deleted_at.is_(None),
                )
                .correlate(Producto)
            )
            if filtros.tiene_alergenos:
                stmt = stmt.where(alergeno_exists)
            else:
                stmt = stmt.where(~alergeno_exists)

        # Count total before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self.session.exec(count_stmt).one()

        # Apply pagination
        offset = (filtros.page - 1) * filtros.size
        paginated_stmt = stmt.offset(offset).limit(filtros.size)
        items = list(self.session.exec(paginated_stmt).all())

        return items, total

    def get_detalle_public(
        self, id: int
    ) -> Optional[tuple[Producto, list[Categoria], list[tuple[ProductoIngrediente, Ingrediente]]]]:
        """Return an active product with its active categories and active ingredients.

        Returns None if the product does not exist or is soft-deleted.
        """
        producto = self.session.exec(
            select(Producto).where(
                Producto.id == id,
                Producto.deleted_at.is_(None),
            )
        ).first()

        if producto is None:
            return None

        # Load active categories
        categorias_stmt = (
            select(Categoria)
            .join(ProductoCategoria, ProductoCategoria.categoria_id == Categoria.id)
            .where(
                ProductoCategoria.producto_id == id,
                Categoria.deleted_at.is_(None),
            )
        )
        categorias = list(self.session.exec(categorias_stmt).all())

        # Load active ingredients with pivot data
        ingredientes_stmt = (
            select(ProductoIngrediente, Ingrediente)
            .join(Ingrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
            .where(
                ProductoIngrediente.producto_id == id,
                Ingrediente.deleted_at.is_(None),
            )
        )
        ingrediente_tuples = list(self.session.exec(ingredientes_stmt).all())

        return producto, categorias, ingrediente_tuples
