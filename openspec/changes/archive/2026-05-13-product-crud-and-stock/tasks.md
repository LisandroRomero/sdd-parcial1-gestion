## 1. Schemas

- [x] 1.1 Agregar `categoria_ids: list[int] = []` a `ProductoCreate` en `backend/productos/schemas.py`
- [x] 1.2 Agregar `categoria_ids: Optional[list[int]] = None` a `ProductoUpdate` en `backend/productos/schemas.py`
- [x] 1.3 Agregar `StockUpdate(BaseModel)` con campo `stock_cantidad: int` y validator `>= 0`
- [x] 1.4 Agregar `DisponibilidadUpdate(BaseModel)` con campo `disponible: bool`
- [x] 1.5 Agregar `ProductoPaginado(BaseModel)` con campos `items: list[ProductoRead]`, `total`, `page`, `size`, `pages`

## 2. Repository

- [x] 2.1 Implementar `ProductoRepository(BaseRepository[Producto])` en `backend/productos/repository.py`
- [x] 2.2 Implementar `get_by_id_active(id: int) -> Optional[Producto]` — retorna None si `deleted_at IS NOT NULL`
- [x] 2.3 Implementar `exists_by_sku(sku: str, exclude_id: Optional[int]) -> bool` — busca SKU activo excluyendo el ID propio
- [x] 2.4 Implementar `sync_categorias(producto_id: int, categoria_ids: list[int]) -> None` — DELETE todos los pivotes actuales del producto y INSERT nuevos con `es_principal=False`
- [x] 2.5 Implementar `get_categoria_ids_activos(categoria_ids: list[int]) -> list[int]` — retorna solo los IDs que existen en la tabla `categoria` con `deleted_at IS NULL`

## 3. Service

- [x] 3.1 Implementar `crear(uow, data: ProductoCreate) -> Producto` — valida SKU único (409), valida categorías existentes (404), crea producto, sync categorías
- [x] 3.2 Implementar `actualizar(uow, id: int, data: ProductoUpdate) -> Producto` — 404 si no existe, 409 si nuevo SKU ya usado, actualiza campos, sync categorías si `categoria_ids` no es None
- [x] 3.3 Implementar `eliminar(uow, id: int) -> None` — 404 si no existe, aplica soft delete `producto.deleted_at = datetime.now(tz=timezone.utc)`
- [x] 3.4 Implementar `cambiar_disponibilidad(uow, id: int, disponible: bool) -> Producto` — 404 si no existe, actualiza `producto.disponible`
- [x] 3.5 Implementar `actualizar_stock(uow, id: int, stock_cantidad: int) -> Producto` — 404 si no existe, valida `>= 0`, actualiza `producto.stock_cantidad`

## 4. Router

- [x] 4.1 Implementar `_get_uow()` local en `backend/productos/router.py` registrando `ProductoRepository` en `uow.repos`
- [x] 4.2 Implementar `POST /` — requiere ADMIN, body `ProductoCreate`, response `201 ProductoRead`
- [x] 4.3 Implementar `PUT /{id}` — requiere ADMIN, body `ProductoUpdate`, response `200 ProductoRead`
- [x] 4.4 Implementar `DELETE /{id}` — requiere ADMIN, response `204 No Content`
- [x] 4.5 Implementar `PATCH /{id}/disponibilidad` — requiere ADMIN o STOCK, body `DisponibilidadUpdate`, response `200 ProductoRead`
- [x] 4.6 Implementar `PATCH /{id}/stock` — requiere ADMIN o STOCK, body `StockUpdate`, response `200 ProductoRead`

## 5. Integración

- [x] 5.1 Importar y registrar `productos_router` en `backend/api/v1/router.py` con prefix `/productos` y tag `productos`

## 6. Verificación

- [x] 6.1 `POST /api/v1/productos` crea producto y retorna `201` con ID y `created_at`
- [x] 6.2 `POST /api/v1/productos` con `categoria_ids` válidos crea los pivotes correctamente
- [x] 6.3 `POST /api/v1/productos` con SKU duplicado retorna `409`
- [x] 6.4 `PUT /api/v1/productos/{id}` actualiza y retorna `200`
- [x] 6.5 `PUT /api/v1/productos/{id}` con nueva lista de `categoria_ids` sincroniza categorías correctamente
- [x] 6.6 `PATCH /api/v1/productos/{id}/disponibilidad` retorna `200` con `disponible` actualizado
- [x] 6.7 `PATCH /api/v1/productos/{id}/stock` retorna `200` con `stock_cantidad` actualizado
- [x] 6.8 `PATCH /api/v1/productos/{id}/stock` con valor negativo retorna `422`
- [x] 6.9 `DELETE /api/v1/productos/{id}` retorna `204` y el producto queda con `deleted_at` poblado
- [x] 6.10 Todos los endpoints protegidos retornan `403` con token de usuario CLIENT
