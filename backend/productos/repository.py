from __future__ import annotations

from typing import Optional

from sqlalchemy import delete
from sqlmodel import Session, select

from backend.core.patterns import BaseRepository
from backend.categorias.model import Categoria
from backend.productos.model import Producto, ProductoCategoria


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

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
