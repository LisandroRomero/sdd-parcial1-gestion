## ADDED Requirements

### Requirement: Frontend expone mapa completo de transiciones admin

El frontend SHALL exponer desde `constants.ts` el mapa `ADMIN_TRANSITIONS` con todas las transiciones admin (incluyendo PENDIENTE) para que los componentes admin consuman la misma fuente de verdad, en lugar de definir mapas locales.

#### Scenario: constants.ts es la fuente única
- **WHEN** cualquier componente admin necesita conocer las transiciones válidas
- **THEN** importa `getAdminNextStates` o `ADMIN_TRANSITIONS` desde `frontend/src/entities/pedidos/constants.ts`

#### Scenario: Mapa sincronizado con backend
- **WHEN** se actualiza `TRANSICIONES_VALIDAS` en `backend/pedidos/service.py`
- **THEN** `ADMIN_TRANSITIONS` en el frontend debe actualizarse manualmente para reflejar los cambios

### MODIFIED Requirements

### Requirement: El sistema valida transiciones de estado según FSM

El sistema SHALL mantener un mapa explícito de transiciones válidas entre estados del pedido. Toda solicitud de cambio de estado SHALL validarse contra este mapa. Los estados terminales (`ENTREGADO`, `CANCELADO`) NO SHALL admitir transiciones salientes.

**Motivo del cambio**: Se agrega un nuevo escenario que refleja la transición de PENDIENTE a CONFIRMADO como válida para el frontend admin (aunque el backend la restrinja por rol a SISTEMA). El frontend muestra todas las opciones y el backend valida según el rol.

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

#### Scenario: Frontend admin muestra transiciones para PENDIENTE
- **WHEN** un ADMIN visualiza pedidos en la tabla o detalle en estado PENDIENTE
- **THEN** el frontend muestra CONFIRMADO y CANCELADO como destinos válidos (según `ADMIN_TRANSITIONS`), y el backend valida según el rol del usuario
