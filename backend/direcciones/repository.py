from __future__ import annotations

from typing import Optional

from sqlalchemy import update
from sqlmodel import select

from backend.core.patterns import BaseRepository
from backend.direcciones.model import DireccionEntrega


class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):
    """Repository for delivery address persistence operations.

    Inherits standard CRUD from ``BaseRepository[DireccionEntrega]``.
    Soft-delete is handled automatically by the base class via ``deleted_at``.
    """

    def list_by_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        """Return all active (non-deleted) addresses for a given user.

        Args:
            usuario_id: PK of the owning user.

        Returns:
            List of active ``DireccionEntrega`` instances.
        """
        stmt = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
        )
        return list(self.session.exec(stmt).all())

    def unset_principal(self, usuario_id: int) -> None:
        """Bulk-set ``es_principal=False`` for all active addresses of a user.

        Uses a bulk UPDATE statement for atomicity. Call this before marking
        a single address as principal to guarantee the one-principal invariant.

        Args:
            usuario_id: PK of the owning user.
        """
        stmt = (
            update(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
            .values(es_principal=False)
        )
        self.session.execute(stmt)

    def get_active(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """Retrieve an active (non-deleted) address by its primary key.

        Args:
            direccion_id: PK of the address.

        Returns:
            ``DireccionEntrega`` if found and not soft-deleted, else ``None``.
        """
        stmt = select(DireccionEntrega).where(
            DireccionEntrega.id == direccion_id,
            DireccionEntrega.deleted_at.is_(None),
        )
        return self.session.exec(stmt).first()
