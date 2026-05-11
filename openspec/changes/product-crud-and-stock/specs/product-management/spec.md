## ADDED Requirements

### Requirement: Crear producto
El sistema SHALL exponer `POST /api/v1/productos` para crear un nuevo producto con sus datos base y opcionalmente asociarlo a categorías. Requiere rol ADMIN.

#### Scenario: Creación exitosa sin categorías
- **WHEN** ADMIN envía body válido sin `categoria_ids`
- **THEN** retorna `201` con `ProductoRead` incluyendo `id`, `codigo_sku`, `precio_base`, `stock_cantidad`, `disponible`, `created_at`

#### Scenario: Creación exitosa con categorías
- **WHEN** ADMIN envía body válido con lista de `categoria_ids` existentes
- **THEN** retorna `201` y los pivotes `ProductoCategoria` son creados con `es_principal=False`

#### Scenario: SKU duplicado
- **WHEN** se envía un `codigo_sku` que ya existe en un producto activo
- **THEN** retorna `409 Conflict` con `code: PRODUCTO_SKU_DUPLICADO`

#### Scenario: Precio negativo o cero
- **WHEN** se envía `precio_base <= 0`
- **THEN** retorna `422 Unprocessable Entity`

#### Scenario: Stock negativo
- **WHEN** se envía `stock_cantidad < 0`
- **THEN** retorna `422 Unprocessable Entity`

#### Scenario: Categoría inexistente en lista
- **WHEN** `categoria_ids` contiene un ID que no corresponde a una categoría activa
- **THEN** retorna `404 Not Found` con los IDs inválidos en el detalle

#### Scenario: Sin rol ADMIN
- **WHEN** un usuario sin rol ADMIN intenta crear un producto
- **THEN** retorna `403 Forbidden`

### Requirement: Actualizar producto
El sistema SHALL exponer `PUT /api/v1/productos/{id}` para actualizar los datos de un producto activo. Requiere rol ADMIN.

#### Scenario: Actualización exitosa de campos básicos
- **WHEN** ADMIN envía campos válidos para un producto existente
- **THEN** retorna `200` con `ProductoRead` actualizado

#### Scenario: Sync de categorías en PUT
- **WHEN** ADMIN envía `categoria_ids` con nueva lista
- **THEN** los pivotes `ProductoCategoria` anteriores se eliminan y se crean los nuevos

#### Scenario: `categoria_ids` ausente en PUT
- **WHEN** ADMIN envía body sin el campo `categoria_ids`
- **THEN** las categorías existentes del producto se preservan sin cambios

#### Scenario: Producto no encontrado
- **WHEN** el `id` no corresponde a un producto activo (`deleted_at IS NULL`)
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: SKU ya usado por otro producto
- **WHEN** el nuevo `codigo_sku` coincide con el de otro producto activo
- **THEN** retorna `409 Conflict` con `code: PRODUCTO_SKU_DUPLICADO`

### Requirement: Eliminar producto (soft delete)
El sistema SHALL exponer `DELETE /api/v1/productos/{id}` que aplica soft delete asignando `deleted_at = now()`. Requiere rol ADMIN.

#### Scenario: Soft delete exitoso
- **WHEN** ADMIN hace `DELETE /api/v1/productos/{id}` con ID existente
- **THEN** retorna `204 No Content` y el producto queda con `deleted_at` poblado

#### Scenario: Producto no encontrado
- **WHEN** el `id` no corresponde a un producto activo
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

### Requirement: Cambiar disponibilidad
El sistema SHALL exponer `PATCH /api/v1/productos/{id}/disponibilidad` para togglear el campo `disponible`. Requiere rol ADMIN o STOCK.

#### Scenario: Toggle exitoso
- **WHEN** ADMIN o STOCK envía `{ "disponible": false }` para un producto activo
- **THEN** retorna `200` con `ProductoRead` donde `disponible = false`

#### Scenario: Producto no encontrado
- **WHEN** el `id` no corresponde a un producto activo
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: Sin rol ADMIN o STOCK
- **WHEN** un usuario CLIENT o sin autenticación intenta cambiar la disponibilidad
- **THEN** retorna `403 Forbidden`

### Requirement: Actualizar stock
El sistema SHALL exponer `PATCH /api/v1/productos/{id}/stock` para setear el `stock_cantidad` de forma absoluta. Requiere rol ADMIN o STOCK.

#### Scenario: Seteo exitoso
- **WHEN** ADMIN o STOCK envía `{ "stock_cantidad": 50 }` para un producto activo
- **THEN** retorna `200` con `ProductoRead` donde `stock_cantidad = 50`

#### Scenario: Stock negativo rechazado
- **WHEN** se envía `stock_cantidad < 0`
- **THEN** retorna `422 Unprocessable Entity`

#### Scenario: Producto no encontrado
- **WHEN** el `id` no corresponde a un producto activo
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

### Requirement: Validación de SKU único
El sistema SHALL garantizar que no existan dos productos activos con el mismo `codigo_sku`. La validación ocurre en el service antes de INSERT o UPDATE.

#### Scenario: SKU libre tras soft delete
- **WHEN** se crea un producto con el mismo `codigo_sku` que uno soft-deleted
- **THEN** la creación DEBE tener éxito (el SKU queda libre tras el soft delete)

### Requirement: Precio con precisión fija
El sistema SHALL almacenar `precio_base` como `DECIMAL(10,2)` y rechazar valores `<= 0`.

#### Scenario: Precio almacenado con exactitud
- **WHEN** se crea un producto con `precio_base = 12.50`
- **THEN** el valor almacenado es exactamente `12.50` (sin pérdida de precisión por float)
