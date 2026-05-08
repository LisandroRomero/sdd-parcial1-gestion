from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import update

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

    def revoke(self, token_id: int) -> None:
        """Revoke a single refresh token by setting revoked_at to now.

        Args:
            token_id: Primary key of the refresh token to revoke.
        """
        token = self.get(token_id)
        if token:
            token.revoked_at = datetime.now(timezone.utc)
            self.session.flush()

    def revoke_all_for_user(self, usuario_id: int) -> None:
        """Revoke all active refresh tokens for a given user (token family invalidation).

        Executes a single bulk UPDATE instead of loading each token individually,
        which avoids N+1 queries when a user has multiple active sessions.

        Args:
            usuario_id: PK of the user whose active tokens should be revoked.
        """
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.usuario_id == usuario_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
            .execution_options(synchronize_session="fetch")
        )
        self.session.execute(stmt)
