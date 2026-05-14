from __future__ import annotations

from typing import Optional

from sqlmodel import Session, func, select

from backend.core.patterns import BaseRepository
from backend.pedidos.model import DetallePedido, HistorialEstadoPedido, Pedido


class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido persistence operations."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id_active(self, id: int) -> Optional[Pedido]:
        """Return a Pedido by primary key.

        Pedido does not have soft-delete, so this delegates to the base get.
        """
        return self.session.get(Pedido, id)

    def get_by_id_with_user_check(self, pedido_id: int, usuario_id: int) -> Optional[Pedido]:
        """Return a Pedido by id if it belongs to the given user, or if user is admin/gestor.

        For now, just check if the pedido exists by id. The caller (service) handles
        role-based access control.
        """
        return self.session.get(Pedido, pedido_id)

    def list_pedidos(
        self,
        usuario_id: Optional[int] = None,
        estado: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Pedido], int]:
        """List pedidos with optional filters. Returns (items, total_count)."""
        query = select(Pedido)
        count_query = select(func.count(Pedido.id))

        if usuario_id is not None:
            query = query.where(Pedido.usuario_id == usuario_id)
            count_query = count_query.where(Pedido.usuario_id == usuario_id)

        if estado is not None:
            query = query.where(Pedido.estado_actual == estado)
            count_query = count_query.where(Pedido.estado_actual == estado)

        total = self.session.exec(count_query).one()

        query = query.order_by(Pedido.created_at.desc()).offset(offset).limit(limit)
        items = list(self.session.exec(query).all())

        return items, total

    def get_historial(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        """Return the state history for a pedido, ordered by created_at ascending."""
        query = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        )
        return list(self.session.exec(query).all())

    def get_productos_by_pedido(self, pedido_id: int) -> list[tuple[int, int]]:
        """Return list of (producto_id, cantidad) for all details in a pedido."""
        query = select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
        detalles = self.session.exec(query).all()
        return [(d.producto_id, d.cantidad) for d in detalles]

    def restaurar_stock_productos(self, productos_stock: list[tuple[int, int]]) -> None:
        """Restore product stock by incrementing each product's stock_cantidad.

        Args:
            productos_stock: List of (producto_id, cantidad) tuples.
        """
        from backend.productos.model import Producto

        # Sort by producto_id to prevent deadlocks (same pattern as order creation)
        productos_stock_sorted = sorted(productos_stock, key=lambda x: x[0])

        for producto_id, cantidad in productos_stock_sorted:
            # Use SELECT FOR UPDATE to lock the row
            stmt = select(Producto).where(Producto.id == producto_id).with_for_update()
            producto = self.session.exec(stmt).first()
            if producto:
                producto.stock_cantidad += cantidad
                self.session.add(producto)


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    """Repository for DetallePedido persistence operations.

    Standard CRUD is provided by BaseRepository.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session)
