### Requirement: Roles ADMIN y STOCK pueden crear, editar y eliminar productos

Los endpoints `POST /api/v1/productos/`, `PUT /api/v1/productos/{id}` y `DELETE /api/v1/productos/{id}` SHALL aceptar tanto el rol ADMIN como el rol STOCK. La implementación actual solo acepta ADMIN en estos endpoints, bloqueando a usuarios con rol STOCK de realizar operaciones que están en su scope de responsabilidad (US-015, US-020, US-022).

#### Scenario: STOCK puede crear un producto

- **WHEN** un usuario con rol STOCK realiza `POST /api/v1/productos/` con datos válidos
- **THEN** el sistema retorna HTTP 201 Created con el producto creado

#### Scenario: STOCK puede editar un producto

- **WHEN** un usuario con rol STOCK realiza `PUT /api/v1/productos/{id}` con datos válidos
- **THEN** el sistema retorna HTTP 200 con el producto actualizado

#### Scenario: STOCK puede eliminar un producto

- **WHEN** un usuario con rol STOCK realiza `DELETE /api/v1/productos/{id}`
- **THEN** el sistema retorna HTTP 204 No Content y el producto queda soft-deleted
