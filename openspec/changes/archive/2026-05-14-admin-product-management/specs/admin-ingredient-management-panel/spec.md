## ADDED Requirements

### Requirement: Panel admin de ingredientes con tabla y CRUD

El sistema SHALL proveer la ruta `/admin/ingredientes` accesible para roles ADMIN y GESTOR_STOCK que muestre una tabla de todos los ingredientes activos con columnas: nombre, es alergeno (badge), fecha. La página SHALL incluir botón "Nuevo ingrediente" y acciones por fila: Editar, Eliminar (con confirmación).

#### Scenario: Admin lista todos los ingredientes

- **WHEN** un usuario con rol ADMIN navega a `/admin/ingredientes`
- **THEN** el sistema muestra una tabla con todos los ingredientes activos

#### Scenario: Admin crea un nuevo ingrediente

- **WHEN** el Admin hace clic en "Nuevo ingrediente", completa nombre y marca si es alergeno, y confirma
- **THEN** el sistema llama a `POST /api/v1/ingredientes/` y el nuevo ingrediente aparece en la tabla

#### Scenario: Admin edita un ingrediente

- **WHEN** el Admin hace clic en "Editar" y modifica nombre o flag de alergeno
- **THEN** el sistema llama a `PUT /api/v1/ingredientes/{id}` y la tabla se refresca

#### Scenario: Admin elimina un ingrediente

- **WHEN** el Admin hace clic en "Eliminar" y confirma el diálogo
- **THEN** el sistema llama a `DELETE /api/v1/ingredientes/{id}` y el ingrediente desaparece de la tabla
