## ADDED Requirements

### Requirement: Create category
El sistema SHALL permitir a usuarios con rol ADMIN o STOCK crear una categoría con nombre obligatorio (máx. 100 caracteres), descripción opcional y `parent_id` opcional (self-ref FK). Un nombre duplicado en el mismo nivel jerárquico SHALL ser rechazado con `HTTP 409`.

#### Scenario: Create root category
- **WHEN** un usuario ADMIN o STOCK envía `POST /api/v1/categorias` con `{"nombre": "Pizzas"}`
- **THEN** el sistema retorna `HTTP 201` con `CategoriaRead` incluyendo `id`, `nombre`, `parent_id: null`

#### Scenario: Create subcategory
- **WHEN** un usuario ADMIN o STOCK envía `POST /api/v1/categorias` con `{"nombre": "Pizzas Vegetarianas", "parent_id": 1}` y el padre existe
- **THEN** el sistema retorna `HTTP 201` con `parent_id: 1` en la respuesta

#### Scenario: Duplicate name at same level rejected
- **WHEN** ya existe una categoría activa "Pizzas" sin padre, y se intenta crear otra "Pizzas" también sin padre
- **THEN** el sistema retorna `HTTP 409` con `code: "CATEGORIA_NOMBRE_DUPLICADO"`

#### Scenario: Unauthenticated request rejected
- **WHEN** se envía `POST /api/v1/categorias` sin Bearer token
- **THEN** el sistema retorna `HTTP 401`

#### Scenario: Insufficient role rejected
- **WHEN** un usuario con rol CLIENT envía `POST /api/v1/categorias`
- **THEN** el sistema retorna `HTTP 403`

---

### Requirement: List categories as tree
El sistema SHALL retornar el árbol completo de categorías activas (sin soft delete) como estructura anidada mediante `GET /api/v1/categorias`. Este endpoint SHALL ser público (sin autenticación). Cada nodo SHALL incluir `id`, `nombre`, `descripcion` y `hijos` (lista recursiva). Nodos raíz (sin padre) aparecen en el nivel superior.

#### Scenario: Empty catalog returns empty array
- **WHEN** no existen categorías activas y se llama `GET /api/v1/categorias`
- **THEN** el sistema retorna `HTTP 200` con `[]`

#### Scenario: Hierarchical tree is returned
- **WHEN** existen categorías con relaciones padre-hijo y se llama `GET /api/v1/categorias`
- **THEN** el sistema retorna `HTTP 200` con árbol anidado: nodos raíz en el nivel superior, subcategorías en `hijos[]`

#### Scenario: Soft-deleted categories are excluded
- **WHEN** una categoría tiene `deleted_at` no nulo
- **THEN** esa categoría no aparece en la respuesta del árbol ni en ninguno de sus niveles

---

### Requirement: Update category
El sistema SHALL permitir a usuarios ADMIN o STOCK actualizar `nombre`, `descripcion` o `parent_id` de una categoría existente. Un cambio de `parent_id` que genere un ciclo SHALL ser rechazado con `HTTP 409`. Asignar una categoría como padre de sí misma SHALL ser rechazado con `HTTP 422`.

#### Scenario: Rename category
- **WHEN** ADMIN envía `PUT /api/v1/categorias/1` con `{"nombre": "Pizzas Artesanales"}`
- **THEN** el sistema retorna `HTTP 200` con `CategoriaRead` actualizado

#### Scenario: Cycle in hierarchy rejected
- **WHEN** existe la cadena A → B → C, y se intenta hacer `PUT /api/v1/categorias/A` con `{"parent_id": C_id}` (C es descendiente de A)
- **THEN** el sistema retorna `HTTP 409` con `code: "CATEGORIA_CICLO_DETECTADO"`

#### Scenario: Self-assignment rejected
- **WHEN** se envía `PUT /api/v1/categorias/5` con `{"parent_id": 5}`
- **THEN** el sistema retorna `HTTP 422` con mensaje de error de validación

#### Scenario: Category not found
- **WHEN** se intenta actualizar una categoría con id inexistente o con `deleted_at` no nulo
- **THEN** el sistema retorna `HTTP 404`

---

### Requirement: Soft delete category
El sistema SHALL permitir a usuarios ADMIN o STOCK eliminar lógicamente una categoría (`deleted_at = now()`). La eliminación SHALL ser rechazada con `HTTP 409` si la categoría tiene: (a) productos activos asociados, o (b) subcategorías activas (sin soft delete). La categoría eliminada SHALL dejar de aparecer en `GET /api/v1/categorias`.

#### Scenario: Delete empty category
- **WHEN** ADMIN envía `DELETE /api/v1/categorias/5` y la categoría no tiene productos activos ni subcategorías activas
- **THEN** el sistema retorna `HTTP 204` y la categoría queda con `deleted_at` no nulo

#### Scenario: Delete rejected with active products
- **WHEN** la categoría tiene al menos un producto con `deleted_at IS NULL` asociado
- **THEN** el sistema retorna `HTTP 409` con `code: "CATEGORIA_CON_PRODUCTOS_ACTIVOS"`

#### Scenario: Delete rejected with active subcategories
- **WHEN** la categoría tiene al menos una subcategoría activa (sin soft delete)
- **THEN** el sistema retorna `HTTP 409` con `code: "CATEGORIA_CON_SUBCATEGORIAS_ACTIVAS"`

#### Scenario: Category not found
- **WHEN** se intenta eliminar una categoría inexistente o ya con `deleted_at` no nulo
- **THEN** el sistema retorna `HTTP 404`
