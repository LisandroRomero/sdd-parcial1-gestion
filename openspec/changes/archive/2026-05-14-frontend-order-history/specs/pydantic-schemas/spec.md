## ADDED Requirements

### Requirement: Schema DireccionSnapshot en respuesta de detalle de pedido

El sistema SHALL incluir un schema `DireccionSnapshot` que exponga los campos de la dirección de entrega asociada al pedido. El schema SHALL incluir: `id`, `calle`, `numero`, `piso` (opcional), `departamento` (opcional), `ciudad`, `provincia`, `codigo_postal` (opcional).

#### Scenario: DireccionSnapshot se serializa correctamente

- **WHEN** se consulta el detalle de un pedido con `direccion_id` válido
- **THEN** el campo `direccion` en la respuesta contiene un objeto con al menos `calle`, `numero`, `ciudad` y `provincia`

#### Scenario: DireccionSnapshot es nulo si la dirección no existe

- **WHEN** se consulta el detalle de un pedido cuya dirección fue eliminada (soft delete activo)
- **THEN** el campo `direccion` en la respuesta es `null`

### Requirement: Campo `cantidad_items` en `PedidoRead`

El sistema SHALL incluir el campo `cantidad_items: int` en el schema `PedidoRead` utilizado en el listado de pedidos. El valor SHALL ser el conteo total de ítems (líneas de detalle) del pedido.

#### Scenario: `cantidad_items` refleja el número de líneas de detalle

- **WHEN** se consulta el listado de pedidos y un pedido tiene 3 líneas de detalle
- **THEN** el campo `cantidad_items` en la respuesta es `3`

#### Scenario: `cantidad_items` es 0 para pedidos sin ítems

- **WHEN** un pedido existe sin líneas de detalle (caso edge)
- **THEN** el campo `cantidad_items` en la respuesta es `0`

### Requirement: Query param `buscar` en `GET /pedidos`

El endpoint `GET /api/v1/pedidos/` SHALL aceptar un query param opcional `buscar: str`. Cuando se provee, SHALL filtrar resultados donde el ID del pedido (como string) contenga el valor buscado. Para roles GESTOR_PEDIDOS y ADMIN, SHALL además buscar en `nombre` y `apellido` del usuario propietario del pedido.

#### Scenario: Búsqueda por ID de pedido devuelve coincidencias

- **WHEN** se realiza `GET /api/v1/pedidos/?buscar=42`
- **THEN** se devuelven solo los pedidos cuyo ID contiene "42" (e.g., ID 42, 142, 420)

#### Scenario: GESTOR busca por nombre de cliente

- **WHEN** un usuario con rol `GESTOR_PEDIDOS` realiza `GET /api/v1/pedidos/?buscar=Juan`
- **THEN** se devuelven los pedidos cuyos propietarios tienen "Juan" en nombre o apellido, además de los que coincidan por ID

#### Scenario: `buscar` vacío o ausente no filtra

- **WHEN** se realiza `GET /api/v1/pedidos/` sin `buscar` o con `buscar=`
- **THEN** no se aplica ningún filtro adicional por búsqueda
