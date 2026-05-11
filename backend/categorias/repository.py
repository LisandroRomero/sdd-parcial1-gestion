from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select, text

from backend.categorias.model import Categoria
from backend.core.patterns import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """Repository for Categoria — extends BaseRepository with hierarchical queries."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id_active(self, id: int) -> Optional[Categoria]:
        """Return an active (non-deleted) category by id, or None."""
        stmt = select(Categoria).where(
            Categoria.id == id,
            Categoria.deleted_at.is_(None),
        )
        return self.session.exec(stmt).first()

    def get_tree(self) -> list[dict]:
        """Return all active categories as flat rows ordered by depth using a recursive CTE.

        Each row contains: id, nombre, descripcion, parent_id, depth.
        The caller is responsible for building the nested tree from these rows.
        """
        sql = text("""
            WITH RECURSIVE cat_tree AS (
                SELECT id, nombre, descripcion, parent_id, 0 AS depth
                FROM categoria
                WHERE parent_id IS NULL AND deleted_at IS NULL
              UNION ALL
                SELECT c.id, c.nombre, c.descripcion, c.parent_id, ct.depth + 1
                FROM categoria c
                JOIN cat_tree ct ON c.parent_id = ct.id
                WHERE c.deleted_at IS NULL
            )
            SELECT id, nombre, descripcion, parent_id, depth
            FROM cat_tree
            ORDER BY depth, nombre;
        """)
        result = self.session.exec(sql)  # type: ignore[call-overload]
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    def exists_name_at_level(
        self,
        nombre: str,
        parent_id: Optional[int],
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Return True if a category with the same nombre exists at the same level.

        The same level means same parent_id (None = root level).
        Excludes ``exclude_id`` to allow updating a category with the same name.
        """
        stmt = select(Categoria).where(
            Categoria.nombre == nombre,
            Categoria.deleted_at.is_(None),
        )
        if parent_id is None:
            stmt = stmt.where(Categoria.parent_id.is_(None))
        else:
            stmt = stmt.where(Categoria.parent_id == parent_id)

        if exclude_id is not None:
            stmt = stmt.where(Categoria.id != exclude_id)

        return self.session.exec(stmt).first() is not None

    def has_ancestor_cycle(self, target_id: int, new_parent_id: int) -> bool:
        """Return True if setting new_parent_id on target_id would create a cycle.

        Walks the ancestor chain from new_parent_id upward. If target_id appears
        in that chain, a cycle would be created.
        """
        sql = text("""
            WITH RECURSIVE ancestors AS (
                SELECT id, parent_id
                FROM categoria
                WHERE id = :new_parent_id
              UNION ALL
                SELECT c.id, c.parent_id
                FROM categoria c
                JOIN ancestors a ON c.id = a.parent_id
                WHERE c.deleted_at IS NULL
            )
            SELECT id FROM ancestors WHERE id = :target_id;
        """)
        result = self.session.exec(  # type: ignore[call-overload]
            sql.bindparams(new_parent_id=new_parent_id, target_id=target_id)
        )
        return result.first() is not None

    def count_active_products(self, categoria_id: int) -> int:
        """Return the number of active products linked to this category via ProductoCategoria."""
        sql = text("""
            SELECT COUNT(*)
            FROM productocategoria pc
            JOIN producto p ON p.id = pc.producto_id
            WHERE pc.categoria_id = :categoria_id
              AND p.deleted_at IS NULL;
        """)
        result = self.session.exec(  # type: ignore[call-overload]
            sql.bindparams(categoria_id=categoria_id)
        )
        return result.scalar() or 0

    def count_active_hijos(self, categoria_id: int) -> int:
        """Return the number of active direct subcategories."""
        stmt = select(Categoria).where(
            Categoria.parent_id == categoria_id,
            Categoria.deleted_at.is_(None),
        )
        return len(self.session.exec(stmt).all())
