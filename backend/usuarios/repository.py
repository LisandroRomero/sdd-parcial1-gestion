from __future__ import annotations

from backend.core.patterns import BaseRepository
from backend.usuarios.model import Usuario


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
