## ADDED Requirements

### Requirement: Consultar pagos de un pedido

El sistema SHALL exponer `GET /api/v1/pagos/{pedido_id}` para usuarios autenticados con rol CLIENT o ADMIN, que retorne todos los intentos de pago asociados a un pedido, incluyendo `mp_status`, `monto`, `mp_payment_id`, `external_reference` y `created_at` de cada intento.

#### Scenario: Cliente consulta pagos de su propio pedido

- **WHEN** un usuario CLIENT autenticado realiza `GET /api/v1/pagos/{pedido_id}` sobre un pedido que le pertenece y que tiene pagos registrados
- **THEN** el sistema retorna HTTP 200 con una lista de objetos `PagoResponse`, ordenados por `created_at` descendente, incluyendo `mp_status`, `monto`, `mp_payment_id`, `external_reference` y `created_at`

#### Scenario: Cliente consulta pagos de pedido ajeno retorna 404

- **WHEN** un usuario CLIENT autenticado realiza `GET /api/v1/pagos/{pedido_id}` sobre un pedido que no le pertenece
- **THEN** el sistema retorna HTTP 404 Not Found, sin revelar si el pedido existe

#### Scenario: Pedido inexistente retorna 404

- **WHEN** un usuario autenticado realiza `GET /api/v1/pagos/{pedido_id}` con un `pedido_id` que no existe
- **THEN** el sistema retorna HTTP 404 Not Found

#### Scenario: Admin consulta pagos de cualquier pedido

- **WHEN** un usuario ADMIN autenticado realiza `GET /api/v1/pagos/{pedido_id}` sobre un pedido de cualquier usuario
- **THEN** el sistema retorna HTTP 200 con la lista de pagos del pedido

#### Scenario: Pedido sin pagos retorna lista vacía

- **WHEN** un usuario autenticado realiza `GET /api/v1/pagos/{pedido_id}` sobre un pedido que no tiene ningún pago registrado
- **THEN** el sistema retorna HTTP 200 con una lista vacía

### Requirement: Enforce ownership on payment query

El sistema SHALL verificar que el pedido pertenezca al usuario autenticado al consultar los pagos. Si el usuario es ADMIN, SHALL permitir consultar pagos de cualquier pedido.

#### Scenario: Cliente ve solo sus propios pedidos

- **WHEN** un usuario CLIENT autenticado realiza `GET /api/v1/pagos/{pedido_id}` para un pedido de otro usuario
- **THEN** el sistema retorna HTTP 404 Not Found

#### Scenario: Admin ve pagos de cualquier pedido

- **WHEN** un usuario ADMIN autenticado realiza `GET /api/v1/pagos/{pedido_id}` para un pedido de cualquier usuario
- **THEN** el sistema retorna HTTP 200 con la lista de pagos
