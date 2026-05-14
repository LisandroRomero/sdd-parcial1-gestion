## ADDED Requirements

### Requirement: Listado de catálogo con opción de incluir soft-deleted para ADMIN y STOCK

Los endpoints de listado `GET /api/v1/productos/`, `GET /api/v1/categorias/` y `GET /api/v1/ingredientes/` SHALL aceptar el query param `include_deleted: bool = false` cuando el usuario autenticado tiene rol ADMIN o STOCK. Cuando `include_deleted=true`, el listado SHALL incluir ítems con `deleted_at IS NOT NULL`. Para usuarios sin esos roles, el param SHALL ser ignorado y solo se mostrarán ítems activos.

#### Scenario: ADMIN lista productos incluyendo eliminados

- **WHEN** un usuario ADMIN realiza `GET /api/v1/productos/?include_deleted=true`
- **THEN** el sistema retorna productos activos y soft-deleted (con `deleted_at` no nulo) en la misma lista paginada

#### Scenario: CLIENT no puede ver productos eliminados

- **WHEN** un usuario CLIENT realiza `GET /api/v1/productos/?include_deleted=true`
- **THEN** el sistema ignora el param y retorna solo productos activos (comportamiento idéntico sin el param)

#### Scenario: Panel admin muestra toggle "Mostrar eliminados"

- **WHEN** un usuario ADMIN accede a `/admin/productos`, `/admin/categorias` o `/admin/ingredientes`
- **THEN** la página muestra un toggle/checkbox "Mostrar eliminados" que, al activarse, recarga la tabla incluyendo ítems eliminados con un badge "Eliminado" visible
