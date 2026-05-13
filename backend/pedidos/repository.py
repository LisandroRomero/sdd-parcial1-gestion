from __future__ import annotations

from typing import Optional

from sqlmodel import Session

from backend.core.patterns import BaseRepository
from backend.pedidos.model import DetallePedido, Pedido


class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido persistence operations."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id_active(self, id: int) -> Optional[Pedido]:
        """Return a Pedido by primary key.

        Pedido does not have soft-delete, so this delegates to the base get.
        """
        return self.session.get(Pedido, id)


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    """Repository for DetallePedido persistence operations.

    Standard CRUD is provided by BaseRepository.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session)
