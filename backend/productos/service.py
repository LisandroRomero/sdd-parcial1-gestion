
from __future__ import annotations

import math
from datetime import datetime, timezone

from fastapi import HTTPException, status

from backend.core.uow import UnitOfWork
from backend.productos.model import Producto
from backend.productos.schemas import (
    ProductoCreate,
    ProductoDetalleRead,
    ProductoFiltros,
    ProductoPaginado,
    ProductoRead,
    ProductoUpdate,
)
from backend.ingredientes.schemas import ProductoIngredienteRead
from backend.categorias.schemas import CategoriaRead


def crear(uow: UnitOfWork, data: ProductoCreate) -> Producto:
    """Create a new product.

    Validates:
    - Unique active SKU.
    - All categoria_ids (if provided) exist and are active.
    """
    repo = uow.repos.productos

    if repo.exists_by_sku(data.codigo_sku):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PRODUCTO_SKU_DUPLICADO: Ya existe un producto activo con ese codigo_sku",
        )

    if data.categoria_ids:
        active_ids = set(repo.get_categoria_ids_activos(data.categoria_ids))
        requested_ids = set(data.categoria_ids)
        invalid_ids = sorted(requested_ids - active_ids)
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"CATEGORIA_IDS_INVALIDOS: Categorías no encontradas o eliminadas: {invalid_ids}"
                ),
            )

    producto = Producto(
        codigo_sku=data.codigo_sku,
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio_base=data.precio_base,
        stock_cantidad=data.stock_cantidad,
        disponible=data.disponible,
        imagen_url=data.imagen_url,
    )
    producto = repo.add(producto)

    if data.categoria_ids:
        repo.sync_categorias(producto.id, data.categoria_ids)  # type: ignore[arg-type]

    return producto


def actualizar(uow: UnitOfWork, id: int, data: ProductoUpdate) -> Producto:
    """Update an existing active product."""
    repo = uow.repos.productos

    producto = repo.get_by_id_active(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTO_NOT_FOUND: Producto no encontrado",
        )

    # Validate categories first to avoid persisting partial updates on error.
    if data.categoria_ids is not None:
        active_ids = set(repo.get_categoria_ids_activos(data.categoria_ids))
        requested_ids = set(data.categoria_ids)
        invalid_ids = sorted(requested_ids - active_ids)
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"CATEGORIA_IDS_INVALIDOS: Categorías no encontradas o eliminadas: {invalid_ids}"
                ),
            )

    if data.codigo_sku is not None and data.codigo_sku != producto.codigo_sku:
        if repo.exists_by_sku(data.codigo_sku, exclude_id=id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="PRODUCTO_SKU_DUPLICADO: Ya existe un producto activo con ese codigo_sku",
            )
        producto.codigo_sku = data.codigo_sku

    if data.nombre is not None:
        producto.nombre = data.nombre
    if data.descripcion is not None:
        producto.descripcion = data.descripcion
    if data.precio_base is not None:
        producto.precio_base = data.precio_base
    if data.stock_cantidad is not None:
        producto.stock_cantidad = data.stock_cantidad
    if data.disponible is not None:
        producto.disponible = data.disponible
    if data.imagen_url is not None:
        producto.imagen_url = data.imagen_url

    producto = repo.update(producto)

    if data.categoria_ids is not None:
        repo.sync_categorias(producto.id, data.categoria_ids)  # type: ignore[arg-type]

    return producto


def eliminar(uow: UnitOfWork, id: int) -> None:
    """Soft-delete a product."""
    repo = uow.repos.productos

    producto = repo.get_by_id_active(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTO_NOT_FOUND: Producto no encontrado",
        )

    producto.deleted_at = datetime.now(tz=timezone.utc)
    repo.update(producto)


def cambiar_disponibilidad(uow: UnitOfWork, id: int, disponible: bool) -> Producto:
    """Set availability flag."""
    repo = uow.repos.productos

    producto = repo.get_by_id_active(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTO_NOT_FOUND: Producto no encontrado",
        )

    producto.disponible = disponible
    return repo.update(producto)


def actualizar_stock(uow: UnitOfWork, id: int, stock_cantidad: int) -> Producto:
    """Set stock quantity (absolute)."""
    repo = uow.repos.productos

    producto = repo.get_by_id_active(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTO_NOT_FOUND: Producto no encontrado",
        )

    producto.stock_cantidad = stock_cantidad
    return repo.update(producto)


def listar_publico(uow: UnitOfWork, filtros: ProductoFiltros) -> ProductoPaginado:
    """Return a paginated public product list filtered by ProductoFiltros."""
    repo = uow.repos.productos
    items, total = repo.list_public(filtros)
    pages = math.ceil(total / filtros.size) if filtros.size > 0 else 0
    return ProductoPaginado(
        items=[ProductoRead.model_validate(p) for p in items],
        total=total,
        page=filtros.page,
        size=filtros.size,
        pages=pages,
    )


def obtener_detalle_publico(uow: UnitOfWork, id: int) -> ProductoDetalleRead:
    """Return a single active product with its categories, ingredients and alergeno flag."""
    repo = uow.repos.productos
    result = repo.get_detalle_public(id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTO_NOT_FOUND: Producto no encontrado",
        )

    producto, categorias, ingrediente_tuples = result

    ingredientes_read = [
        ProductoIngredienteRead(
            ingrediente_id=pi.ingrediente_id,
            nombre=ing.nombre,
            es_alergeno=ing.es_alergeno,
            cantidad=pi.cantidad,
            unidad=pi.unidad,
            es_removible=pi.es_removible,
        )
        for pi, ing in ingrediente_tuples
    ]

    tiene_alergenos = any(ing.es_alergeno for _, ing in ingrediente_tuples)

    detalle = ProductoDetalleRead(
        **ProductoRead.model_validate(producto).model_dump(),
        categorias=[CategoriaRead.model_validate(c) for c in categorias],
        ingredientes=ingredientes_read,
        tiene_alergenos=tiene_alergenos,
    )
    return detalle
