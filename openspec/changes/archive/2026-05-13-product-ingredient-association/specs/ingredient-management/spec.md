## MODIFIED Requirements

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
