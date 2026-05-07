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
