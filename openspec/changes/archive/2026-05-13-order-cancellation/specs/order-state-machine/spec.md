## MODIFIED Requirements

### Requirement: Las transiciones validan el rol del usuario

El sistema SHALL validar que el rol del usuario autenticado tenga permiso para ejecutar la transición solicitada, según la matriz de roles por transición. Si el usuario no tiene el rol requerido, la transición SHALL ser rechazada.

Además, el frontend SHALL mostrar u ocultar el botón "Cancelar pedido" según el `estado_actual` del pedido y el `rol` del usuario autenticado, siguiendo las reglas de visibilidad definidas.

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

#### Scenario: CLIENTE ve botón cancelar en PENDIENTE
- **WHEN** un usuario con rol `CLIENTE` visualiza un pedido propio con `estado_actual = "PENDIENTE"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: CLIENTE no ve botón cancelar en CONFIRMADO
- **WHEN** un usuario con rol `CLIENTE` visualiza un pedido propio con `estado_actual = "CONFIRMADO"`
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible

#### Scenario: ADMIN ve botón cancelar en EN_PREP
- **WHEN** un usuario con rol `ADMIN` visualiza un pedido con `estado_actual = "EN_PREP"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: GESTOR_PEDIDOS ve botón cancelar en CONFIRMADO
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` visualiza un pedido con `estado_actual = "CONFIRMADO"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: GESTOR_PEDIDOS no ve botón cancelar en EN_PREP
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` visualiza un pedido con `estado_actual = "EN_PREP"`
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible

#### Scenario: GESTOR_STOCK no ve botón cancelar en ningún estado
- **WHEN** un usuario con rol `GESTOR_STOCK` visualiza cualquier pedido
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible en ningún estado

---

### Requirement: Cancelación con motivo obligatorio

El sistema SHALL requerir un `motivo` no vacío cuando se cancela un pedido (destino `"CANCELADO"`). Si no se proporciona motivo, la solicitud SHALL ser rechazada.

#### Scenario: Cancelación con motivo válido
- **WHEN** se cancela un pedido incluyendo `motivo = "El cliente ya no quiere el producto"`
- **THEN** el sistema acepta la cancelación y persiste el motivo en el historial

#### Scenario: Cancelación sin motivo
- **WHEN** se cancela un pedido sin incluir `motivo` o con `motivo = ""`
- **THEN** el sistema rechaza con `422 Unprocessable Entity` y error `PEDIDO_MOTIVO_REQUERIDO`

---

### Requirement: Cancelar pedido vía DELETE endpoint

El sistema SHALL exponer `DELETE /api/v1/pedidos/{id}` con query param `motivo` obligatorio. Este endpoint SHALL ser un atajo semántico que fuerza `nuevo_estado = "CANCELADO"`.

#### Scenario: Cancelación exitosa
- **WHEN** se envía `DELETE /api/v1/pedidos/1?motivo=El%20cliente%20cancela`
- **THEN** el sistema responde `200 OK` con el `PedidoRead` actualizado a `estado_actual = "CANCELADO"`

#### Scenario: Cancelación sin motivo
- **WHEN** se envía `DELETE /api/v1/pedidos/1` sin `motivo`
- **THEN** el sistema responde `422 Unprocessable Entity` con error `PEDIDO_MOTIVO_REQUERIDO`
