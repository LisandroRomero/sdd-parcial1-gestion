## ADDED Requirements

### Requirement: Asociar ingrediente a producto
El sistema SHALL exponer `POST /api/v1/productos/{id}/ingredientes` para agregar un ingrediente a un producto con `ingrediente_id`, `cantidad` (opcional, float) y `unidad` (opcional, string ≤20 chars). Requiere rol ADMIN o STOCK.

#### Scenario: Asociación exitosa
- **WHEN** ADMIN o STOCK envía `{ ingrediente_id, cantidad, unidad }` válidos para un producto activo y un ingrediente activo
- **THEN** retorna `201 Created` con `ProductoIngredienteRead` incluyendo `ingrediente_id`, `nombre`, `es_alergeno`, `cantidad`, `unidad`, `es_removible`

#### Scenario: Producto no encontrado o inactivo
- **WHEN** el `id` del producto no existe o tiene `deleted_at` poblado
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: Ingrediente no encontrado o inactivo
- **WHEN** el `ingrediente_id` no existe o tiene `deleted_at` poblado
- **THEN** retorna `404 Not Found` con `code: INGREDIENTE_NOT_FOUND`

#### Scenario: Asociación duplicada
- **WHEN** el par `(producto_id, ingrediente_id)` ya existe en `producto_ingredientes`
- **THEN** retorna `409 Conflict` con `code: PRODUCTO_INGREDIENTE_DUPLICADO`

#### Scenario: Sin autenticación o rol insuficiente
- **WHEN** un usuario sin rol ADMIN o STOCK hace la petición
- **THEN** retorna `403 Forbidden`

### Requirement: Listar ingredientes de un producto
El sistema SHALL exponer `GET /api/v1/productos/{id}/ingredientes` retornando la lista completa de ingredientes asociados al producto, incluyendo información del ingrediente (nombre, es_alergeno). Acceso público.

#### Scenario: Lista con ingredientes
- **WHEN** se hace `GET /api/v1/productos/{id}/ingredientes` para un producto activo con ingredientes asociados
- **THEN** retorna `200 OK` con `{ items: [ProductoIngredienteRead], total: N }` incluyendo nombre e `es_alergeno` de cada ingrediente

#### Scenario: Producto sin ingredientes
- **WHEN** se hace `GET /api/v1/productos/{id}/ingredientes` para un producto activo sin asociaciones
- **THEN** retorna `200 OK` con `{ items: [], total: 0 }`

#### Scenario: Producto no encontrado
- **WHEN** el `id` del producto no existe o está soft-deleted
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: Ingredientes soft-deleted no aparecen en la lista
- **WHEN** un ingrediente asociado al producto fue soft-deleted posteriormente
- **THEN** ese ingrediente NO aparece en la lista (JOIN filtra por `ingrediente.deleted_at IS NULL`)

### Requirement: Remover ingrediente de un producto
El sistema SHALL exponer `DELETE /api/v1/productos/{id}/ingredientes/{ingrediente_id}` para eliminar la asociación entre un producto y un ingrediente. Requiere rol ADMIN o STOCK.

#### Scenario: Remoción exitosa
- **WHEN** ADMIN o STOCK hace `DELETE /api/v1/productos/{id}/ingredientes/{ingrediente_id}` y la asociación existe
- **THEN** retorna `204 No Content` y la fila es eliminada de `producto_ingredientes`

#### Scenario: Asociación no encontrada
- **WHEN** el par `(producto_id, ingrediente_id)` no existe en `producto_ingredientes`
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_INGREDIENTE_NOT_FOUND`

#### Scenario: Producto no encontrado
- **WHEN** el `id` del producto no existe o está soft-deleted
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: Sin autenticación o rol insuficiente
- **WHEN** un usuario sin rol ADMIN o STOCK hace la petición
- **THEN** retorna `403 Forbidden`

### Requirement: Validación de existencia y estado activo
El sistema SHALL validar que tanto el producto como el ingrediente estén activos (`deleted_at IS NULL`) antes de crear cualquier asociación. La validación SHALL ocurrir en el service antes de delegar al repositorio.

#### Scenario: No se puede asociar a producto eliminado
- **WHEN** se intenta asociar un ingrediente a un producto con `deleted_at` poblado
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND` antes de hacer INSERT

#### Scenario: No se puede asociar ingrediente eliminado
- **WHEN** se intenta asociar un ingrediente con `deleted_at` poblado a un producto activo
- **THEN** retorna `404 Not Found` con `code: INGREDIENTE_NOT_FOUND` antes de hacer INSERT
