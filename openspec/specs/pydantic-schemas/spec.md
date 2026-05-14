## ADDED Requirements

### Requirement: Schemas Pydantic para Usuario

El sistema SHALL definir schemas Create/Update/Read para Usuario. Create SHALL incluir validación de email (formato), password con longitud mínima 8 caracteres, nombre, apellido, telefono opcional. Update SHALL permitir modificación parcial. Read SHALL excluir password_hash.

#### Scenario: Creación de usuario con validación de email
- **WHEN** se envía un UsuarioCreate con email inválido
- **THEN** SHALL rechazar con error de validación Pydantic

#### Scenario: Lectura de usuario sin password_hash
- **WHEN** se serializa un UsuarioRead
- **THEN** SHALL excluir el campo password_hash de la respuesta

### Requirement: Schemas Pydantic para Rol y UsuarioRol

El sistema SHALL definir schemas Create (solo super-admin) y Read para Rol. Para UsuarioRol, schema de asignación con usuario_id + rol_codigo.

#### Scenario: Asignación de rol
- **WHEN** se crea un UsuarioRol
- **THEN** SHALL requerir usuario_id y rol_codigo, ambos válidos

### Requirement: Schemas Pydantic para RefreshToken

El sistema SHALL definir schema Read para RefreshToken y schema Create con token y expires_at.

#### Scenario: RefreshToken no expone token_hash en lectura
- **WHEN** se serializa un RefreshToken
- **THEN** SHALL devolver datos sin el hash interno

### Requirement: Schemas Pydantic para DireccionEntrega

El sistema SHALL definir schemas Create/Update/Read con validación de campos requeridos (alias, linea1, ciudad, codigo_postal).

#### Scenario: Creación de dirección
- **WHEN** se crea una dirección
- **THEN** SHALL requerir alias, linea1, ciudad, codigo_postal

### Requirement: Schemas Pydantic para Categoria

El sistema SHALL definir schemas Create/Update/Read con soporte para jerarquía (parent_id opcional) y soft-delete no expuesto en Create.

#### Scenario: Creación de categoría con padre
- **WHEN** se crea una Categoria con parent_id
- **THEN** SHALL validar que el parent_id existe

### Requirement: Schemas Pydantic para Producto

El sistema SHALL definir schemas Create/Update/Read con precio_base DECIMAL(10,2), stock_cantidad INT >= 0, disponible BOOLEAN, e imagen_url opcional.

#### Scenario: Precio base con precisión decimal
- **WHEN** se crea un Producto con precio_base
- **THEN** SHALL aceptar hasta 2 decimales y validar que sea > 0

#### Scenario: Stock no negativo
- **WHEN** se crea o actualiza stock_cantidad
- **THEN** SHALL validar que sea >= 0

### Requirement: Schemas Pydantic para Ingrediente

El sistema SHALL definir schemas Create/Update/Read con nombre VARCHAR(100) y es_alergeno BOOLEAN.

#### Scenario: Nombre de ingrediente único
- **WHEN** se crea un Ingrediente
- **THEN** SHALL validar que el nombre no esté duplicado (validación a nivel servicio, no schema)

### Requirement: Schemas Pydantic para Pedido y DetallePedido

El sistema SHALL definir schemas Create (con lista de detalles), Update (solo campos permitidos según FSM), y Read (con detalles embebidos y total calculado).

#### Scenario: Creación de pedido con detalles
- **WHEN** se crea un PedidoCreate
- **THEN** SHALL incluir lista de DetallePedidoCreate con producto_id, cantidad, y personalizacion opcional

#### Scenario: Lectura de pedido incluye detalles
- **WHEN** se serializa un PedidoRead
- **THEN** SHALL incluir la lista de DetallePedidoRead embebida

### Requirement: Schemas Pydantic para Pago

El sistema SHALL definir schemas PagoCreate (con pedido_id, monto) y PagoRead (con mp_payment_id, mp_status, external_reference).

#### Scenario: Pago sin exponer datos sensibles
- **WHEN** se serializa un PagoRead
- **THEN** SHALL NO incluir idempotency_key en respuestas públicas

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
