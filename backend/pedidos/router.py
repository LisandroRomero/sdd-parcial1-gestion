from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.core.database import engine
from backend.core.dependencies import require_role
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.direcciones.repository import DireccionEntregaRepository
from backend.pedidos import service as pedido_service
from backend.pedidos.repository import DetallePedidoRepository, PedidoRepository
from backend.pedidos.schemas import PedidoCreate, PedidoRead
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
