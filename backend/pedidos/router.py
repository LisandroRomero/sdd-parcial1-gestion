from __future__ import annotations

from collections.abc import Generator
from math import ceil

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from backend.core.database import engine
from backend.core.dependencies import get_current_user, require_role
from backend.core.exceptions import AppException, ForbiddenException, NotFoundException
from backend.core.uow import UnitOfWork
from backend.direcciones.repository import DireccionEntregaRepository
from backend.pedidos import service as pedido_service
from backend.pedidos.repository import DetallePedidoRepository, PedidoRepository
from backend.pedidos.schemas import (
    AvanzarEstadoRequest,
    DetallePedidoRead,
    HistorialEstadoRead,
    PagoResumen,
    PedidoCreate,
    PedidoDetail,
    PedidoListRead,
    PedidoRead,
)
from backend.productos.repository import ProductoRepository
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers pedidos, detalles_pedido, productos,
# and direcciones repositories
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork for the pedidos module."""
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("pedidos", lambda s: PedidoRepository(s))
    uow.repos.register("detalles_pedido", lambda s: DetallePedidoRepository(s))
    uow.repos.register("productos", lambda s: ProductoRepository(s))
    uow.repos.register("direcciones", lambda s: DireccionEntregaRepository(s))
    try:
        yield uow
    except (HTTPException, AppException):
        uow.session.commit()
        raise
    except Exception:
        uow.session.rollback()
        raise
    finally:
        uow.session.close()


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.post(
    "/",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
def crear_pedido(
    body: PedidoCreate,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(require_role("CLIENT")),
) -> PedidoRead:
    pedido = pedido_service.crear_pedido(uow, body, current_user)
    uow.commit()
    return PedidoRead.model_validate(pedido)


@router.patch(
    "/{id}/estado",
    response_model=PedidoRead,
    summary="Advance order state",
)
def avanzar_estado_endpoint(
    id: int,
    body: AvanzarEstadoRequest,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(require_role("ADMIN", "PEDIDOS", "CLIENT")),
) -> PedidoRead:
    pedido = pedido_service.avanzar_estado(uow, id, body.nuevo_estado, current_user)
    uow.commit()
    return PedidoRead.model_validate(pedido)


@router.delete(
    "/{id}",
    response_model=PedidoRead,
    summary="Cancel an order",
)
def cancelar_pedido_endpoint(
    id: int,
    motivo: str = Query(..., description="Cancellation reason (required)"),
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(require_role("ADMIN", "PEDIDOS", "CLIENT")),
) -> PedidoRead:
    pedido = pedido_service.cancelar_pedido(uow, id, motivo, current_user)
    uow.commit()
    return PedidoRead.model_validate(pedido)


@router.get(
    "/{id}",
    response_model=PedidoDetail,
    summary="Get order by ID",
)
def get_pedido(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> PedidoDetail:
    pedido = uow.repos.pedidos.get(id)
    if pedido is None:
        raise NotFoundException("PEDIDO_NOT_FOUND")

    # CLIENT users can only see their own orders
    user_roles = {ur.rol_codigo for ur in current_user.roles}
    if "CLIENT" in user_roles and len(user_roles) == 1 and pedido.usuario_id != current_user.id:
        raise ForbiddenException("PEDIDO_NO_AUTORIZADO")

    # Build PagoResumen from the first associated payment (if any)
    pago_resumen: Optional[PagoResumen] = None
    if pedido.pagos:
        pago = pedido.pagos[0]
        pago_resumen = PagoResumen(
            id=pago.id,
            estado_pago=pago.mp_status,
            metodo_pago=pedido.forma_pago_codigo,
            monto=pago.monto,
        )

    return PedidoDetail(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        estado_actual=pedido.estado_actual,
        total=pedido.total,
        costo_envio=pedido.costo_envio,
        created_at=pedido.created_at,
        detalles=[DetallePedidoRead.model_validate(d) for d in pedido.detalles],
        historial_estados=[HistorialEstadoRead.model_validate(h) for h in pedido.historial_estados],
        pago=pago_resumen,
    )


@router.get(
    "/",
    response_model=PedidoListRead,
    summary="List orders",
)
def list_pedidos(
    estado: Optional[str] = Query(default=None, description="Filter by state"),
    fecha_desde: Optional[str] = Query(default=None, description="Filter by start date (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(default=None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    # Backward compatible params (deprecated)
    limit: Optional[int] = Query(default=None, ge=1, le=100, description="[DEPRECATED] Use size instead"),
    offset: Optional[int] = Query(default=None, ge=0, description="[DEPRECATED] Use page instead"),
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> PedidoListRead:
    user_roles = {ur.rol_codigo for ur in current_user.roles}

    # CLIENT users only see their own orders
    usuario_id: Optional[int] = None
    if user_roles == {"CLIENT"}:
        usuario_id = current_user.id

    # Backward compatibility: if limit/offset provided, convert to page/size
    if limit is not None:
        size = limit
    if offset is not None:
        page = (offset // size) + 1

    items, total = uow.repos.pedidos.list_pedidos(
        usuario_id=usuario_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=size,
        offset=(page - 1) * size,
    )

    return PedidoListRead(
        items=[PedidoRead.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0,
    )


@router.get(
    "/{id}/historial",
    response_model=list[HistorialEstadoRead],
    summary="Get order state history",
)
def get_historial_pedido(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> list[HistorialEstadoRead]:
    pedido = uow.repos.pedidos.get(id)
    if pedido is None:
        raise NotFoundException("PEDIDO_NOT_FOUND")

    user_roles = {ur.rol_codigo for ur in current_user.roles}
    if "CLIENT" in user_roles and len(user_roles) == 1 and pedido.usuario_id != current_user.id:
        raise ForbiddenException("PEDIDO_NO_AUTORIZADO")

    historial = uow.repos.pedidos.get_historial(id)
    return [HistorialEstadoRead.model_validate(h) for h in historial]
