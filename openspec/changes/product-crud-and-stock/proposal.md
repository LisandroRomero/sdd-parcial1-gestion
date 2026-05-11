## Why

El módulo `backend/productos/` tiene el modelo `Producto` completo (con `deleted_at`, `stock_cantidad`, `disponible`, `precio_base DECIMAL`) y schemas Pydantic base, pero `repository.py`, `service.py` y `router.py` están vacíos (0 bytes). Sin esta implementación no hay forma de crear ni gestionar el catálogo — requisito bloqueante para pedidos, pagos y el panel admin. Además los schemas actuales carecen de `StockUpdate`, `DisponibilidadUpdate` y soporte de `categoria_ids` en creación.

## What Changes

- Implementar `ProductoRepository` con consultas por SKU, filtros de stock y disponibilidad.
- Implementar `ProductoService` con validaciones de negocio (precio > 0, stock ≥ 0, SKU único).
- Implementar `ProductoRouter` con los endpoints de administración:
  - `POST /api/v1/productos` (ADMIN) — crear producto + asociar categorías opcionales
  - `PUT /api/v1/productos/{id}` (ADMIN) — actualizar datos del producto + sync categorías
  - `DELETE /api/v1/productos/{id}` (ADMIN) — soft delete
  - `PATCH /api/v1/productos/{id}/disponibilidad` (ADMIN, STOCK) — toggle disponible
  - `PATCH /api/v1/productos/{id}/stock` (ADMIN, STOCK) — actualizar stock_cantidad
- Agregar schemas `StockUpdate` y `DisponibilidadUpdate`.
- Agregar campo `categoria_ids: list[int]` a `ProductoCreate` y `ProductoUpdate`.
- Registrar el router en `api/v1/router.py`.

## Capabilities

### New Capabilities
- `product-management`: CRUD administrativo de productos con gestión de stock, disponibilidad y asociación de categorías. Endpoints `POST/PUT/DELETE /api/v1/productos` + `PATCH /disponibilidad` + `PATCH /stock`.

### Modified Capabilities
- `pydantic-schemas`: agregar `StockUpdate`, `DisponibilidadUpdate`; extender `ProductoCreate` y `ProductoUpdate` con `categoria_ids: list[int]`.

## Impact

- **Backend:** `backend/productos/` — `schemas.py`, `repository.py`, `service.py`, `router.py`
- **App:** `backend/api/v1/router.py` — registro del router `/api/v1/productos`
- **Dependencia upstream:** Epic 2.4 (`product-ingredient-association`) usa `ProductoRepository` para validar que el producto existe antes de asociar ingredientes.
- **Dependencia upstream:** Epic 2.5 (`public-product-catalog`) usa `ProductoRepository` para listar y detallar productos públicamente.
- **Dependencia upstream:** Epic 5.1 (`order-creation-with-uow`) usa `uow.repos.productos.get_by_id()` para leer `precio_base` y `disponible` al crear pedidos.
