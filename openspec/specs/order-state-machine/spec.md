### Requirement: El sistema valida transiciones de estado según FSM

El sistema SHALL mantener un mapa explícito de transiciones válidas entre estados del pedido. Toda solicitud de cambio de estado SHALL validarse contra este mapa. Los estados terminales (`ENTREGADO`, `CANCELADO`) NO SHALL admitir transiciones salientes.

#### Scenario: Transición válida de CONFIRMADO a EN_PREP
- **WHEN** un pedido con `estado_actual = "CONFIRMADO"` recibe una solicitud de avance a `"EN_PREP"`
- **THEN** el sistema acepta la transición y actualiza el estado

#### Scenario: Transición inválida de PENDIENTE a ENTREGADO
- **WHEN** se intenta avanzar un pedido de `"PENDIENTE"` a `"ENTREGADO"` (salta estados intermedios)
- **THEN** el sistema rechaza con `422 Unprocessable Entity` y error `PEDIDO_TRANSICION_INVALIDA`

#### Scenario: Transición desde estado terminal es rechazada
- **WHEN** se intenta avanzar un pedido con `estado_actual = "ENTREGADO"` o `"CANCELADO"`
- **THEN** el sistema rechaza con `409 Conflict` y error `PEDIDO_ESTADO_TERMINAL`

#### Scenario: Estado destino no existe en el mapa
- **WHEN** se solicita una transición a un código de estado que no existe en `EstadoPedido`
- **THEN** el sistema rechaza con `422 Unprocessable Entity` y error `PEDIDO_ESTADO_INEXISTENTE`

### Requirement: Las transiciones validan el rol del usuario

El sistema SHALL validar que el rol del usuario autenticado tenga permiso para ejecutar la transición solicitada, según la matriz de roles por transición. Si el usuario no tiene el rol requerido, la transición SHALL ser rechazada.

#### Scenario: GESTOR_PEDIDOS avanza de CONFIRMADO a EN_PREP
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` solicita avanzar un pedido de `"CONFIRMADO"` a `"EN_PREP"`
- **THEN** el sistema acepta la transición (rol autorizado)

#### Scenario: CLIENTE intenta avanzar de CONFIRMADO a EN_PREP
- **WHEN** un usuario con rol `CLIENTE` solicita avanzar un pedido de `"CONFIRMADO"` a `"EN_PREP"`
- **THEN** el sistema rechaza con `403 Forbidden` y error `PEDIDO_ROL_NO_AUTORIZADO`

#### Scenario: ADMIN cancela desde EN_PREP
- **WHEN** un usuario con rol `ADMIN` solicita cancelar un pedido en estado `"EN_PREP"`
- **THEN** el sistema acepta la transición (rol autorizado)

#### Scenario: GESTOR_PEDIDOS intenta cancelar desde EN_PREP
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` solicita cancelar un pedido en estado `"EN_PREP"`
- **THEN** el sistema rechaza con `403 Forbidden` y error `PEDIDO_ROL_NO_AUTORIZADO`

### Requirement: Cancelación con motivo obligatorio

El sistema SHALL requerir un `motivo` no vacío cuando se cancela un pedido (destino `"CANCELADO"`). Si no se proporciona motivo, la solicitud SHALL ser rechazada.

#### Scenario: Cancelación con motivo válido
- **WHEN** se cancela un pedido incluyendo `motivo = "El cliente ya no quiere el producto"`
- **THEN** el sistema acepta la cancelación y persiste el motivo en el historial

#### Scenario: Cancelación sin motivo
- **WHEN** se cancela un pedido sin incluir `motivo` o con `motivo = ""`
- **THEN** el sistema rechaza con `422 Unprocessable Entity` y error `PEDIDO_MOTIVO_REQUERIDO`

### Requirement: Rollback de stock al cancelar

El sistema SHALL restaurar el stock de cada producto en el pedido cuando se cancela un pedido que ya había descontado stock (estados `CONFIRMADO` o posteriores). Si el pedido está en `PENDIENTE` (stock aún no descontado), no SHALL modificar stock.

#### Scenario: Cancelación de pedido CONFIRMADO restaura stock
- **WHEN** se cancela un pedido en estado `"CONFIRMADO"` que tenía 2 unidades del producto P1
- **THEN** `Producto.stock_cantidad` de P1 se incrementa en 2 (vuelve al valor anterior)

#### Scenario: Cancelación de pedido PENDIENTE no modifica stock
- **WHEN** se cancela un pedido en estado `"PENDIENTE"`
- **THEN** el stock de los productos no se modifica (nunca se descontó)

#### Scenario: Rollback atómico con SELECT FOR UPDATE
- **WHEN** se cancela un pedido y se restaura stock
- **THEN** la operación SHALL usar `SELECT ... FOR UPDATE` sobre los productos a modificar, dentro de la misma transacción del UoW

### Requirement: Avanzar estado vía PATCH endpoint

El sistema SHALL exponer `PATCH /api/v1/pedidos/{id}/estado` que recibe un `AvanzarEstadoRequest` con `nuevo_estado` y `motivo` opcional. El endpoint SHALL validar la transición y registrar el cambio en el historial.

#### Scenario: Avance exitoso con historial
- **WHEN** se envía `PATCH /api/v1/pedidos/1/estado` con `{"nuevo_estado": "EN_PREP"}` siendo el estado actual `"CONFIRMADO"`
- **THEN** el sistema responde `200 OK` con el `PedidoRead` actualizado y se inserta un registro en `HistorialEstadoPedido` con `estado_desde = "CONFIRMADO"`, `estado_hasta = "EN_PREP"`, `usuario_id` del usuario autenticado, y `created_at` actual

#### Scenario: Pedido no encontrado
- **WHEN** se envía `PATCH /api/v1/pedidos/999/estado`
- **THEN** el sistema responde `404 Not Found` con error `PEDIDO_NOT_FOUND`

### Requirement: Cancelar pedido vía DELETE endpoint

El sistema SHALL exponer `DELETE /api/v1/pedidos/{id}` con query param `motivo` obligatorio. Este endpoint SHALL ser un atajo semántico que fuerza `nuevo_estado = "CANCELADO"`.

#### Scenario: Cancelación exitosa
- **WHEN** se envía `DELETE /api/v1/pedidos/1?motivo=El%20cliente%20cancela`
- **THEN** el sistema responde `200 OK` con el `PedidoRead` actualizado a `estado_actual = "CANCELADO"`

#### Scenario: Cancelación sin motivo
- **WHEN** se envía `DELETE /api/v1/pedidos/1` sin `motivo`
- **THEN** el sistema responde `422 Unprocessable Entity` con error `PEDIDO_MOTIVO_REQUERIDO`

### Requirement: Consultar pedido por ID con historial

El sistema SHALL exponer `GET /api/v1/pedidos/{id}` que devuelve el `PedidoRead` completo incluyendo su `historial_estados` ordenado por `created_at` ascendente.

#### Scenario: Pedido existe
- **WHEN** se envía `GET /api/v1/pedidos/1`
- **THEN** el sistema responde `200 OK` con el `PedidoRead` que incluye el campo `historial_estados` con todas las entradas del historial

#### Scenario: Pedido no existe
- **WHEN** se envía `GET /api/v1/pedidos/999`
- **THEN** el sistema responde `404 Not Found` con error `PEDIDO_NOT_FOUND`

#### Scenario: Pedido de otro usuario (CLIENTE)
- **WHEN** un usuario CLIENTE solicita un pedido que pertenece a otro usuario
- **THEN** el sistema responde `403 Forbidden` con error `PEDIDO_NO_AUTORIZADO`

### Requirement: Listar pedidos del usuario

El sistema SHALL exponer `GET /api/v1/pedidos/` que lista los pedidos del usuario autenticado. Para roles ADMIN y GESTOR_PEDIDOS, SHALL listar todos los pedidos. SHALL soportar filtros opcionales por `estado` y paginación (`limit`, `offset`).

#### Scenario: CLIENTE lista sus pedidos
- **WHEN** un usuario CLIENTE envía `GET /api/v1/pedidos/`
- **THEN** el sistema responde `200 OK` con solo los pedidos donde `usuario_id` coincide con el usuario autenticado

#### Scenario: ADMIN lista todos los pedidos
- **WHEN** un usuario ADMIN envía `GET /api/v1/pedidos/`
- **THEN** el sistema responde `200 OK` con todos los pedidos del sistema

#### Scenario: Filtrar por estado
- **WHEN** se envía `GET /api/v1/pedidos/?estado=PENDIENTE`
- **THEN** el sistema responde solo los pedidos con `estado_actual = "PENDIENTE"`

### Requirement: Consultar historial de un pedido

El sistema SHALL exponer `GET /api/v1/pedidos/{id}/historial` que devuelve el audit trail completo del pedido ordenado por `created_at` ascendente. Cada entrada SHALL incluir `estado_desde`, `estado_hasta`, `usuario_id` (o null), `motivo` (o null), y `created_at`.

#### Scenario: Historial de pedido con múltiples transiciones
- **WHEN** se envía `GET /api/v1/pedidos/1/historial` para un pedido con 3 cambios de estado
- **THEN** el sistema responde `200 OK` con un array de 3 entradas ordenadas cronológicamente

### Requirement: Schema AvanzarEstadoRequest

El sistema SHALL definir un schema Pydantic `AvanzarEstadoRequest` con campos `nuevo_estado: str` y `motivo: Optional[str]`. El schema SHALL validar que `motivo` no sea vacío si está presente.

#### Scenario: Validación de motivo vacío
- **WHEN** se envía `{"nuevo_estado": "CANCELADO", "motivo": ""}`
- **THEN** el sistema rechaza con `422 Unprocessable Entity` por campo inválido

### Requirement: HistorialEstadoPedido registra quién y por qué

El sistema SHALL almacenar en `HistorialEstadoPedido` el `usuario_id` del usuario que ejecutó la transición (o `NULL` si fue el sistema) y un `motivo` opcional. La tabla SHALL ser append-only (solo `created_at`, sin `updated_at`).

#### Scenario: Transición manual registra usuario
- **WHEN** un usuario autenticado avanza el estado de un pedido
- **THEN** el historial registra `usuario_id` del usuario que ejecutó la acción

#### Scenario: Transición del sistema registra NULL
- **WHEN** el sistema cambia el estado automáticamente (reservado para webhook)
- **THEN** el historial registra `usuario_id = NULL`

#### Scenario: Historial append-only
- **WHEN** se consulta un historial existente
- **THEN** cada entrada tiene `created_at` único y `updated_at` NO existe como campo
