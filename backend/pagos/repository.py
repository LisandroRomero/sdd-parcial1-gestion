from __future__ import annotations

from sqlmodel import select

from backend.core.patterns import BaseRepository
from backend.pagos.model import Pago


class PagoRepository(BaseRepository[Pago]):
    """Repository for Pago entity operations."""

    def get_by_pedido(self, pedido_id: int) -> list[Pago]:
        """Return all payments for a given order, newest first.

        Args:
            pedido_id: The order ID.

        Returns:
            List of Pago instances ordered by created_at DESC.
        """
        stmt = (
            select(Pago)
            .where(Pago.pedido_id == pedido_id)
            .order_by(Pago.created_at.desc())
        )
        return list(self.session.exec(stmt).all())

    def get_by_idempotency_key(self, key: str) -> Pago | None:
        """Retrieve a payment by its idempotency key.

        Args:
            key: The idempotency key to look up.

        Returns:
            The matching Pago, or None if not found.
        """
        return self.get_by(idempotency_key=key)

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Pago | None:
        """Retrieve a payment by its MercadoPago payment ID.

        Args:
            mp_payment_id: The MercadoPago payment ID.

        Returns:
            The matching Pago, or None if not found.
        """
        return self.get_by(mp_payment_id=mp_payment_id)
