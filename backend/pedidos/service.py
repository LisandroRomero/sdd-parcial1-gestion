from __future__ import annotations

from decimal import Decimal

from backend.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from backend.core.uow import UnitOfWork
from backend.pedidos.model import DetallePedido, HistorialEstadoPedido, Pedido
from backend.pedidos.schemas import PedidoCreate
from backend.usuarios.model import Usuario

# Mapa de transiciones válidas: {estado_origen: {estado_destino: set[roles_permitidos]}}
# Roles: "CLIENT", "ADMIN", "PEDIDOS", "SISTEMA" (reservado para webhooks)
TRANSICIONES_VALIDAS: dict[str, dict[str, set[str]]] = {
    "PENDIENTE": {
        "CONFIRMADO": {"SISTEMA", "ADMIN"},        # Webhook MP — pago aprobado
        "CANCELADO": {"CLIENT", "ADMIN", "PEDIDOS"},
    },
    "CONFIRMADO": {
        "EN_PREP": {"PEDIDOS", "ADMIN"},
        "CANCELADO": {"ADMIN", "PEDIDOS"},
    },
    "EN_PREP": {
        "EN_CAMINO": {"PEDIDOS", "ADMIN"},
        "CANCELADO": {"ADMIN"},           # Solo ADMIN puede cancelar desde preparación
    },
    "EN_CAMINO": {
        "ENTREGADO": {"PEDIDOS", "ADMIN"},
    },
}


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
        forma_pago_codigo=data.forma_pago_codigo,
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


def _validar_transicion(estado_actual: str, nuevo_estado: str, roles_usuario: set[str]) -> None:
    """Validate a state transition against the FSM map and user roles.

    Raises:
        ConflictException: If the current state is terminal.
        ValidationException: If the transition doesn't exist in the FSM map.
        ForbiddenException: If the user's roles don't permit this transition.
    """
    # Check if current state has any transitions defined (terminal check)
    if estado_actual not in TRANSICIONES_VALIDAS:
        raise ConflictException(
            f"PEDIDO_ESTADO_TERMINAL: El pedido está en estado terminal '{estado_actual}'"
        )

    # Check if the target state is a valid transition from current state
    transiciones_destino = TRANSICIONES_VALIDAS.get(estado_actual, {})
    if nuevo_estado not in transiciones_destino:
        raise ValidationException(
            f"PEDIDO_TRANSICION_INVALIDA: No se puede transicionar de '{estado_actual}' a '{nuevo_estado}'"
        )

    # Check if user has the required role
    roles_permitidos = transiciones_destino[nuevo_estado]
    if not roles_usuario.intersection(roles_permitidos):
        raise ForbiddenException(
            f"PEDIDO_ROL_NO_AUTORIZADO: Se requiere uno de los roles: {', '.join(roles_permitidos)}"
        )


def avanzar_estado(
    uow: UnitOfWork,
    pedido_id: int,
    nuevo_estado: str,
    usuario_actual: Usuario,
) -> Pedido:
    """Advance an order to a new state after validating the FSM transition.

    Flow:
    1. Load pedido (404 if not found).
    2. Validate transition + role.
    3. Insert HistorialEstadoPedido entry.
    4. Update pedido.estado_actual.
    5. Return refreshed pedido.
    """
    pedido = uow.repos.pedidos.get(pedido_id)
    if pedido is None:
        raise NotFoundException("PEDIDO_NOT_FOUND")

    user_roles = {ur.rol_codigo for ur in usuario_actual.roles}

    _validar_transicion(pedido.estado_actual, nuevo_estado, user_roles)

    # Create history entry
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=pedido.estado_actual,
        estado_hasta=nuevo_estado,
        usuario_id=usuario_actual.id,
        motivo=None,  # Sin motivo en avance normal
    )
    uow.session.add(historial)

    # Update pedido state
    pedido.estado_actual = nuevo_estado
    uow.repos.pedidos.update(pedido)
    uow.session.flush()

    uow.session.refresh(pedido)
    return pedido


def cancelar_pedido(
    uow: UnitOfWork,
    pedido_id: int,
    motivo: str,
    usuario_actual: Usuario,
) -> Pedido:
    """Cancel an order with mandatory reason.

    Flow:
    1. Load pedido (404 if not found).
    2. Validate motivo is provided.
    3. Validate transition + role.
    4. Restore stock if pedido was already confirmed (stock was deducted).
    5. Insert HistorialEstadoPedido entry with motivo.
    6. Update pedido.estado_actual = "CANCELADO".
    7. Return refreshed pedido.
    """
    # Validate motivo
    if not motivo or not motivo.strip():
        raise ValidationException("PEDIDO_MOTIVO_REQUERIDO: El motivo es obligatorio para cancelar un pedido")

    pedido = uow.repos.pedidos.get(pedido_id)
    if pedido is None:
        raise NotFoundException("PEDIDO_NOT_FOUND")

    user_roles = {ur.rol_codigo for ur in usuario_actual.roles}

    _validar_transicion(pedido.estado_actual, "CANCELADO", user_roles)

    # Restore stock if the order had stock deducted (CONFIRMADO or beyond)
    # PENDIENTE hasn't deducted stock yet
    estados_con_stock_descontado = {"CONFIRMADO", "EN_PREP", "EN_CAMINO"}
    if pedido.estado_actual in estados_con_stock_descontado:
        productos_stock = uow.repos.pedidos.get_productos_by_pedido(pedido_id)
        uow.repos.pedidos.restaurar_stock_productos(productos_stock)

    # Create history entry
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=pedido.estado_actual,
        estado_hasta="CANCELADO",
        usuario_id=usuario_actual.id,
        motivo=motivo.strip(),
    )
    uow.session.add(historial)

    # Update pedido state
    pedido.estado_actual = "CANCELADO"
    uow.repos.pedidos.update(pedido)
    uow.session.flush()

    uow.session.refresh(pedido)
    return pedido
