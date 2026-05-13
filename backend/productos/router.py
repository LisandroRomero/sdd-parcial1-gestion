from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.core.database import engine
from backend.core.dependencies import require_role
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.productos import service as producto_service
from backend.productos.repository import ProductoRepository
from backend.productos.schemas import (
    DisponibilidadUpdate,
    ProductoCreate,
    ProductoRead,
    ProductoUpdate,
    StockUpdate,
)
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers ProductoRepository
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork with ProductoRepository registered."""
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("productos", lambda s: ProductoRepository(s))
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
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def crear_producto(
    body: ProductoCreate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN")),
) -> ProductoRead:
    producto = producto_service.crear(uow, body)
    uow.commit()
    return ProductoRead.model_validate(producto)


@router.put(
    "/{id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
)
def actualizar_producto(
    id: int,
    body: ProductoUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN")),
) -> ProductoRead:
    producto = producto_service.actualizar(uow, id, body)
    uow.commit()
    return ProductoRead.model_validate(producto)


@router.delete(
    "/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a product",
)
def eliminar_producto(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN")),
) -> Response:
    producto_service.eliminar(uow, id)
    uow.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{id}/disponibilidad",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Set product availability",
)
def cambiar_disponibilidad(
    id: int,
    body: DisponibilidadUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> ProductoRead:
    producto = producto_service.cambiar_disponibilidad(uow, id, body.disponible)
    uow.commit()
    return ProductoRead.model_validate(producto)


@router.patch(
    "/{id}/stock",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Set product stock quantity",
)
def actualizar_stock(
    id: int,
    body: StockUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> ProductoRead:
    producto = producto_service.actualizar_stock(uow, id, body.stock_cantidad)
    uow.commit()
    return ProductoRead.model_validate(producto)
