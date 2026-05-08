from __future__ import annotations

from sqlalchemy import delete, func
from sqlmodel import select

from backend.core.patterns import BaseRepository
from backend.usuarios.model import Usuario, UsuarioRol


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository for Usuario entity operations."""

    def get_by_email(self, email: str) -> Usuario | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to look up.

        Returns:
            The matching Usuario, or None if not found.
        """
        return self.get_by(email=email)

    def count_by_role(self, rol_codigo: str) -> int:
        """Count how many users have the given role code assigned.

        Args:
            rol_codigo: The role code to count (e.g. 'ADMIN', 'CLIENT').

        Returns:
            Number of UsuarioRol rows matching the role code.
        """
        stmt = select(func.count()).select_from(UsuarioRol).where(
            UsuarioRol.rol_codigo == rol_codigo
        )
        result = self.session.exec(stmt)
        return result.one()


class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    """Repository for UsuarioRol entity operations."""

    def delete_all_for_user(self, usuario_id: int) -> None:
        """Delete all role assignments for a given user.

        Uses a bulk DELETE statement to avoid loading records into memory.

        Args:
            usuario_id: The ID of the user whose roles will be removed.
        """
        stmt = delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        self.session.execute(stmt)
