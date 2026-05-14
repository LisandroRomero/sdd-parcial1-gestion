from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlmodel import select

from backend.core.patterns import BaseRepository
from backend.usuarios.model import Usuario, UsuarioRol


class AdminRepository(BaseRepository[Usuario]):
    """Repository for admin-side user management queries.

    All queries operate over the ``usuario`` table.  They intentionally
    duplicate column access from ``UsuarioRepository`` — this is a
    deliberate design decision (D2 in design.md) to avoid cross-module
    coupling between the admin and usuarios modules.
    """

    def list_usuarios(
        self,
        buscar: Optional[str] = None,
        rol: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Usuario], int]:
        """Return a paginated list of users with optional search and role filter.

        Args:
            buscar: Optional free-text search applied via ``ilike`` over
                ``nombre``, ``apellido``, and ``email``.
            rol: Optional role code to filter by (joined to ``UsuarioRol``).
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            A tuple of ``(items, total_count)`` — items is the paginated slice,
            total_count is the full unfiltered count matching the filters.
        """
        # --- Build base statement ----------------------------------------
        stmt = select(Usuario)

        if rol is not None:
            stmt = stmt.join(
                UsuarioRol,
                (UsuarioRol.usuario_id == Usuario.id) & (UsuarioRol.rol_codigo == rol),
            )

        if buscar is not None:
            pattern = f"%{buscar}%"
            stmt = stmt.where(
                Usuario.nombre.ilike(pattern)  # type: ignore[union-attr]
                | Usuario.apellido.ilike(pattern)  # type: ignore[union-attr]
                | Usuario.email.ilike(pattern)
            )

        # --- Count query (same filters, no pagination) --------------------
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self.session.exec(count_stmt).one()

        # --- Data query (with pagination) ---------------------------------
        items = list(
            self.session.exec(stmt.offset(offset).limit(limit)).all()
        )

        return items, total

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Retrieve a user by primary key.

        Args:
            usuario_id: Primary key of the user.

        Returns:
            The matching ``Usuario``, or ``None`` if not found.
        """
        return self.session.get(Usuario, usuario_id)
