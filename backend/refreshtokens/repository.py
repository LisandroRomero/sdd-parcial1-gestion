from __future__ import annotations

from datetime import datetime

from backend.core.patterns import BaseRepository
from backend.refreshtokens.model import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken entity operations."""

    def create(
        self,
        usuario_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a new refresh token record.

        Args:
            usuario_id: FK to the owning usuario.
            token_hash: SHA-256 hex digest of the JWT refresh token string.
            expires_at: Timezone-aware datetime when the token expires.

        Returns:
            The newly created RefreshToken instance.
        """
        refresh_token = RefreshToken(
            usuario_id=usuario_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return self.add(refresh_token)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve a refresh token by its SHA-256 hash.

        Args:
            token_hash: SHA-256 hex digest to look up.

        Returns:
            The matching RefreshToken, or None if not found.
        """
        return self.get_by(token_hash=token_hash)
