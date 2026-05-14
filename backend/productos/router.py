from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from backend.core.database import engine
from backend.core.dependencies import get_current_user_optional, require_role
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.ingredientes import service as ingrediente_service
from backend.ingredientes.repository import IngredienteRepository
from backend.ingredientes.schemas import (
    ProductoIngredienteCreate,
    ProductoIngredienteListResponse,
    ProductoIngredienteRead,
)
from backend.productos import service as producto_service
from backend.productos.repository import ProductoRepository
from backend.productos.schemas import (
    DisponibilidadUpdate,
    ProductoCreate,
    ProductoDetalleRead,
    ProductoFiltros,
    ProductoPaginado,
    ProductoRead,
    ProductoUpdate,
    StockUpdate,
)
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers ProductoRepository + IngredienteRepository
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork with ProductoRepository and IngredienteRepository registered."""
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("productos", lambda s: ProductoRepository(s))
    uow.repos.register("ingredientes", lambda s: IngredienteRepository(s))
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


@router.get(
    "/",
    response_model=ProductoPaginado,
    status_code=status.HTTP_200_OK,
    summary="List public products with optional filters",
)
def listar_productos_publico(
    filtros: ProductoFiltros = Depends(),
    include_deleted: bool = Query(default=False),
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Optional[Usuario] = Depends(get_current_user_optional),
) -> ProductoPaginado:
    effective_include = include_deleted
    if effective_include:
        user_roles = {ur.rol_codigo for ur in current_user.roles} if current_user else set()
        if not user_roles.intersection({"ADMIN", "STOCK"}):
            effective_include = False

    return producto_service.listar_publico(uow, filtros, include_deleted=effective_include)


@router.get(
    "/{id}",
    response_model=ProductoDetalleRead,
    status_code=status.HTTP_200_OK,
    summary="Get public product detail with categories and ingredients",
)
def obtener_producto_publico(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
) -> ProductoDetalleRead:
    return producto_service.obtener_detalle_publico(uow, id)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def crear_producto(
    body: ProductoCreate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
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
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
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
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
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


# ------------------------------------------------------------------
# Product-ingredient association endpoints
# ------------------------------------------------------------------


@router.post(
    "/{id}/ingredientes",
    response_model=ProductoIngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Associate an ingredient with a product",
)
def agregar_ingrediente(
    id: int,
    body: ProductoIngredienteCreate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> ProductoIngredienteRead:
    result = ingrediente_service.asociar_ingrediente(uow, id, body)
    uow.commit()
    return result


@router.get(
    "/{id}/ingredientes",
    response_model=ProductoIngredienteListResponse,
    status_code=status.HTTP_200_OK,
    summary="List ingredients of a product",
)
def listar_ingredientes(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
) -> ProductoIngredienteListResponse:
    return ingrediente_service.listar_ingredientes_producto(uow, id)


@router.delete(
    "/{id}/ingredientes/{ingrediente_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an ingredient from a product",
)
def remover_ingrediente(
    id: int,
    ingrediente_id: int,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> Response:
    ingrediente_service.desasociar_ingrediente(uow, id, ingrediente_id)
    uow.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
