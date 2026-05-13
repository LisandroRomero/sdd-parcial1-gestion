### Requirement: Listar ingredientes
El sistema SHALL exponer `GET /api/v1/ingredientes` retornando una lista paginada de ingredientes activos (`deleted_at IS NULL`). Soporta filtro opcional `?es_alergeno=true|false`. Acceso público.

#### Scenario: Listado sin filtro
- **WHEN** se hace `GET /api/v1/ingredientes?page=1&size=20`
- **THEN** retorna `200` con `{ items, total, page, size, pages }` con todos los ingredientes activos

#### Scenario: Filtro por alergeno
- **WHEN** se hace `GET /api/v1/ingredientes?es_alergeno=true`
- **THEN** retorna solo ingredientes donde `es_alergeno = true` y `deleted_at IS NULL`

#### Scenario: Base de datos vacía
- **WHEN** no existen ingredientes activos
- **THEN** retorna `200` con `{ items: [], total: 0, page: 1, size: 20, pages: 0 }`

### Requirement: Crear ingrediente
El sistema SHALL exponer `POST /api/v1/ingredientes` para crear un nuevo ingrediente. Requiere rol ADMIN o STOCK.

#### Scenario: Creación exitosa
- **WHEN** ADMIN o STOCK envía `{ nombre, es_alergeno }` con nombre único
- **THEN** retorna `201` con `IngredienteRead` incluyendo `id` y `created_at`

#### Scenario: Nombre duplicado
- **WHEN** se intenta crear un ingrediente con un nombre que ya existe (`deleted_at IS NULL`)
- **THEN** retorna `409 Conflict` con `code: INGREDIENT_NAME_EXISTS`

#### Scenario: Nombre vacío o ausente
- **WHEN** se envía `nombre = ""` o el campo está ausente
- **THEN** retorna `422 Unprocessable Entity`

#### Scenario: Sin autenticación o rol insuficiente
- **WHEN** un usuario sin rol ADMIN o STOCK hace `POST /api/v1/ingredientes`
- **THEN** retorna `403 Forbidden`

### Requirement: Actualizar ingrediente
El sistema SHALL exponer `PUT /api/v1/ingredientes/{id}` para actualizar nombre y/o `es_alergeno`. Requiere rol ADMIN o STOCK.

#### Scenario: Actualización exitosa
- **WHEN** ADMIN o STOCK envía campos válidos para un ingrediente existente
- **THEN** retorna `200` con el `IngredienteRead` actualizado

#### Scenario: Ingrediente no encontrado
- **WHEN** el `id` no corresponde a un ingrediente activo
- **THEN** retorna `404 Not Found` con `code: INGREDIENT_NOT_FOUND`

#### Scenario: Nombre ya usado por otro ingrediente
- **WHEN** el nuevo nombre coincide con el de otro ingrediente activo
- **THEN** retorna `409 Conflict` con `code: INGREDIENT_NAME_EXISTS`

### Requirement: Eliminar ingrediente (soft delete)
El sistema SHALL exponer `DELETE /api/v1/ingredientes/{id}` que aplica soft delete asignando `deleted_at = now()`. El ingrediente desaparece de listados, no puede ser asociado a nuevos productos, y sus asociaciones históricas a `ProductoIngrediente` se preservan pero ya no aparecen en `GET /api/v1/productos/{id}/ingredientes` (la consulta filtra por `ingrediente.deleted_at IS NULL`). Requiere rol ADMIN o STOCK.

#### Scenario: Soft delete exitoso
- **WHEN** ADMIN o STOCK hace `DELETE /api/v1/ingredientes/{id}` con ID existente
- **THEN** retorna `204 No Content` y el ingrediente queda con `deleted_at` poblado

#### Scenario: Ingrediente ya eliminado o inexistente
- **WHEN** el `id` no corresponde a un ingrediente activo (`deleted_at IS NULL`)
- **THEN** retorna `404 Not Found` con `code: INGREDIENT_NOT_FOUND`

#### Scenario: El ingrediente eliminado no aparece en listados de ingredientes
- **WHEN** se consulta `GET /api/v1/ingredientes` tras el soft delete
- **THEN** el ingrediente eliminado NO está en el resultado

#### Scenario: El ingrediente eliminado no puede ser asociado a un producto
- **WHEN** se intenta hacer `POST /api/v1/productos/{id}/ingredientes` con un `ingrediente_id` de un ingrediente soft-deleted
- **THEN** retorna `404 Not Found` con `code: INGREDIENTE_NOT_FOUND`

#### Scenario: El ingrediente eliminado no aparece en la lista de ingredientes del producto
- **WHEN** un ingrediente previamente asociado a un producto es soft-deleted
- **THEN** `GET /api/v1/productos/{id}/ingredientes` NO devuelve ese ingrediente (JOIN filtra `ingrediente.deleted_at IS NULL`)

### Requirement: Validación de unicidad de nombre
El sistema SHALL garantizar que no existan dos ingredientes activos con el mismo nombre (case-sensitive). La validación ocurre en el service antes de delegar al repositorio.

#### Scenario: Unicidad enforced en create
- **WHEN** se crea un ingrediente con nombre idéntico a uno activo existente
- **THEN** retorna `409` antes de hacer INSERT en la base de datos

#### Scenario: Ingrediente eliminado no bloquea reutilización de nombre
- **WHEN** se crea un ingrediente con el mismo nombre que uno soft-deleted
- **THEN** la creación DEBE tener éxito (el nombre queda libre tras el soft delete)
