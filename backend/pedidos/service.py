from __future__ import annotations

from decimal import Decimal

from backend.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from backend.core.uow import UnitOfWork
from backend.pedidos.model import DetallePedido, HistorialEstadoPedido, Pedido
from backend.pedidos.schemas import PedidoCreate
from backend.usuarios.model import Usuario


def crear_pedido(
    uow: UnitOfWork,
    data: PedidoCreate,
    current_user: Usuario,
) -> Pedido:
    """Create an order atomically within a single UoW transaction.

    Flow:
    1. Validate cart is not empty.
    2. Load and verify ownership of delivery address.
    3. Lock each product row (SELECT FOR UPDATE) in a consistent order to
       prevent deadlocks, validate availability and stock.
    4. Insert Pedido, flush to obtain PK.
    5. Insert DetallePedido rows with price snapshots.
    6. Decrement product stock.
    7. Update order total.
    8. Insert HistorialEstadoPedido (estado_desde=NULL, estado_hasta=PENDIENTE).
    9. Return the Pedido instance.
    """

    # -- 5.2: Guard — empty cart ------------------------------------------
    if not data.detalles:
        raise BadRequestException("PEDIDO_CARRITO_VACIO")

    # -- 5.3: Load delivery address ----------------------------------------
    direccion = uow.repos.direcciones.get_active(data.direccion_id)
    if direccion is None:
        raise NotFoundException("PEDIDO_DIRECCION_NOT_FOUND")

    # -- 5.4: Ownership check ----------------------------------------------
    if direccion.usuario_id != current_user.id:
        raise ForbiddenException("PEDIDO_DIRECCION_NO_AUTORIZADA")

    # -- 5.5 & 5.6: Lock products in consistent order (prevents deadlocks) -
    # Sort by producto_id ascending before acquiring row locks.
    detalles_sorted = sorted(data.detalles, key=lambda d: d.producto_id)
    productos_map: dict[int, object] = {}

    for detalle in detalles_sorted:
        producto = uow.repos.productos.get_by_id_active_with_lock(
            detalle.producto_id
        )
        if producto is None or not producto.disponible:
            raise ValidationException(
                f"PEDIDO_PRODUCTO_NO_DISPONIBLE: producto_id={detalle.producto_id}"
            )
        if producto.stock_cantidad < detalle.cantidad:
            raise ValidationException(
                f"PEDIDO_STOCK_INSUFICIENTE: producto_id={detalle.producto_id}, "
                f"disponible={producto.stock_cantidad}"
            )
        productos_map[detalle.producto_id] = producto

    # -- 5.7: Create Pedido instance ---------------------------------------
    pedido = Pedido(
        usuario_id=current_user.id,
        direccion_id=data.direccion_id,
        estado_actual="PENDIENTE",
        total=Decimal("0"),
        costo_envio=Decimal("0"),
        forma_pago_codigo=None,
    )
    uow.repos.pedidos.add(pedido)
    # add() calls flush + refresh, so pedido.id is now populated

    # -- 5.8 & 5.9 & 5.10: Create details, decrement stock ----------------
    detalles_db: list[DetallePedido] = []
    for detalle in data.detalles:
        producto = productos_map[detalle.producto_id]
        detalle_db = DetallePedido(
            pedido_id=pedido.id,
            producto_id=detalle.producto_id,
            nombre_snapshot=producto.nombre,
            precio_snapshot=producto.precio_base,
            cantidad=detalle.cantidad,
            personalizacion=detalle.personalizacion,
            subtotal=producto.precio_base * detalle.cantidad,
        )
        uow.repos.detalles_pedido.add(detalle_db)
        detalles_db.append(detalle_db)

        # Decrement stock
        producto.stock_cantidad -= detalle.cantidad
        uow.repos.productos.update(producto)

    # -- 5.11: Update order total ------------------------------------------
    pedido.total = sum(d.subtotal for d in detalles_db)
    uow.repos.pedidos.update(pedido)

    # -- 5.12: Create initial state history entry --------------------------
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=None,
        estado_hasta="PENDIENTE",
    )
    uow.session.add(historial)
    uow.session.flush()

    # -- 5.13: Return populated pedido ------------------------------------
    uow.session.refresh(pedido)
    return pedido
