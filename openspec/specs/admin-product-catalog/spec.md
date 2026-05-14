### Requirement: Panel admin de productos con tabla y CRUD

El sistema SHALL proveer la ruta `/admin/productos` accesible solo para rol ADMIN que muestre una tabla de todos los productos activos con columnas: nombre, SKU, precio, stock, disponible (badge), fecha. La página SHALL incluir botón "Nuevo producto" que abre un modal de creación, y acciones por fila: Editar (modal), cambiar disponibilidad (toggle), actualizar stock (inline), Eliminar (confirmación).

#### Scenario: Admin lista todos los productos

- **WHEN** un usuario con rol ADMIN navega a `/admin/productos`
- **THEN** el sistema muestra una tabla paginada con todos los productos activos del sistema

#### Scenario: Admin crea un nuevo producto

- **WHEN** el Admin hace clic en "Nuevo producto", completa el formulario (nombre, precio, stock, categoría, descripción) y confirma
- **THEN** el sistema llama a `POST /api/v1/productos/` y el nuevo producto aparece en la tabla

#### Scenario: Admin edita un producto

- **WHEN** el Admin hace clic en "Editar" en una fila y modifica los datos
- **THEN** el sistema llama a `PUT /api/v1/productos/{id}` y la tabla se refresca con los datos actualizados

#### Scenario: Admin actualiza el stock de un producto

- **WHEN** el Admin modifica el campo de stock de un producto y confirma
- **THEN** el sistema llama a `PATCH /api/v1/productos/{id}/stock` con la cantidad nueva

#### Scenario: Admin elimina un producto (soft delete)

- **WHEN** el Admin hace clic en "Eliminar" y confirma el diálogo
- **THEN** el sistema llama a `DELETE /api/v1/productos/{id}` y el producto desaparece de la tabla

#### Scenario: No-ADMIN es redirigido

- **WHEN** un usuario sin rol ADMIN navega a `/admin/productos`
- **THEN** el sistema redirige a la página de inicio
