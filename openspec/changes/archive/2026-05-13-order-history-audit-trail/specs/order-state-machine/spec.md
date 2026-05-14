# Spec: order-state-machine (delta)

## ADDED Requirements

<!-- No new requirements. The only change is the modification of the existing "Consultar historial de un pedido" requirement to add authorization guard. -->

## MODIFIED Requirements

### Requirement: Consultar historial de un pedido

El sistema SHALL exponer `GET /api/v1/pedidos/{id}/historial` que devuelve el audit trail completo del pedido ordenado por `created_at` ascendente. Cada entrada SHALL incluir `estado_desde` (o null), `estado_hasta`, `usuario_id` (o null), `motivo` (o null), y `created_at`.

El endpoint SHALL validar autorización según el rol del usuario autenticado:
- CLIENTE: solo ve historial de sus propios pedidos (`pedido.usuario_id == current_user.id`)
- ADMIN y GESTOR_PEDIDOS: ven historial de cualquier pedido

La primera entrada del historial SHALL tener `estado_desde = NULL` (RN-02).

#### Scenario: Historial de pedido con múltiples transiciones
- **WHEN** se envía `GET /api/v1/pedidos/1/historial` para un pedido con 3 cambios de estado
- **THEN** el sistema responde `200 OK` con un array de 3 entradas ordenadas cronológicamente

#### Scenario: CLIENT ve historial de su propio pedido
- **WHEN** un usuario CLIENTE envía `GET /api/v1/pedidos/{id}/historial` donde el pedido le pertenece
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: CLIENT no ve historial de pedido ajeno
- **WHEN** un usuario CLIENTE envía `GET /api/v1/pedidos/{id}/historial` donde el pedido pertenece a otro usuario
- **THEN** el sistema responde `403 Forbidden` con error `PEDIDO_NO_AUTORIZADO`

#### Scenario: ADMIN ve historial de cualquier pedido
- **WHEN** un usuario ADMIN envía `GET /api/v1/pedidos/{id}/historial` para cualquier pedido
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: GESTOR_PEDIDOS ve historial de cualquier pedido
- **WHEN** un usuario GESTOR_PEDIDOS envía `GET /api/v1/pedidos/{id}/historial` para cualquier pedido
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: Pedido inexistente devuelve 404
- **WHEN** se envía `GET /api/v1/pedidos/99999/historial`
- **THEN** el sistema responde `404 Not Found` con error `PEDIDO_NOT_FOUND`

#### Scenario: Primera entrada con estado_desde NULL
- **WHEN** se consulta el historial de un pedido
- **THEN** la primera entrada (más antigua) tiene `estado_desde = NULL` y `estado_hasta` igual al estado inicial del pedido

## REMOVED Requirements

<!-- None -->
