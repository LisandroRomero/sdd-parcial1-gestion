### Requirement: Panel admin de categorías con tabla y CRUD

El sistema SHALL proveer la ruta `/admin/categorias` accesible para roles ADMIN y GESTOR_STOCK que muestre una tabla de todas las categorías activas con columnas: nombre, descripción, categoría padre (si existe), fecha. La página SHALL incluir botón "Nueva categoría" y acciones por fila: Editar, Eliminar (con confirmación).

#### Scenario: Admin lista todas las categorías

- **WHEN** un usuario con rol ADMIN navega a `/admin/categorias`
- **THEN** el sistema muestra una tabla con todas las categorías activas

#### Scenario: Admin crea una nueva categoría

- **WHEN** el Admin hace clic en "Nueva categoría", completa nombre y opcionalmente descripción y categoría padre, y confirma
- **THEN** el sistema llama a `POST /api/v1/categorias/` y la nueva categoría aparece en la tabla

#### Scenario: Admin edita una categoría

- **WHEN** el Admin hace clic en "Editar" y modifica los datos
- **THEN** el sistema llama a `PUT /api/v1/categorias/{id}` y la tabla se refresca

#### Scenario: Admin elimina una categoría sin productos activos

- **WHEN** el Admin hace clic en "Eliminar" en una categoría sin productos activos y confirma
- **THEN** el sistema llama a `DELETE /api/v1/categorias/{id}` y la categoría desaparece de la tabla

#### Scenario: Eliminar categoría con productos activos retorna error

- **WHEN** el Admin intenta eliminar una categoría que tiene productos activos
- **THEN** el sistema muestra el mensaje de error del backend en el modal
