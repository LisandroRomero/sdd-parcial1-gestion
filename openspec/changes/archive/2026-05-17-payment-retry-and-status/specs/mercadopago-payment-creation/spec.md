## MODIFIED Requirements

### Requirement: Registrar pago en BD con datos completos

El sistema SHALL registrar cada intento de pago en la tabla `Pago` con los siguientes campos: `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference` (UUID único por intento de pago), `idempotency_key`, `monto`, y `moneda`.

#### Scenario: Pago registrado con todos los campos requeridos

- **WHEN** se crea un pago exitosamente
- **THEN** la tabla `Pago` contiene un registro con `pedido_id`, `mp_payment_id no nulo`, `mp_status`, `external_reference = UUID único generado fresh para este intento`, `idempotency_key = UUID generado`, `monto` y `moneda`, y `created_at` con timestamp actual

## ADDED Requirements

### Requirement: Reintentar pago rechazado

El sistema SHALL permitir que un usuario CLIENT o ADMIN realice un nuevo intento de pago sobre un pedido que está en estado `PENDIENTE` y cuyo pago anterior fue rechazado (`mp_status = "rejected"`), generando una nueva `idempotency_key` y un nuevo `external_reference` único, preservando todos los registros de intentos previos.

#### Scenario: Retry con pago anterior rechazado

- **WHEN** un usuario CLIENT autenticado realiza `POST /api/v1/pagos/crear` con un `pedido_id` en estado `PENDIENTE` que tiene al menos un pago previo con `mp_status = "rejected"`
- **THEN** el sistema genera un nuevo UUID como `idempotency_key` y un nuevo UUID como `external_reference`, llama a la API de MercadoPago, registra el nuevo `Pago` en BD, y retorna HTTP 201 con `PagoResponse`

#### Scenario: Retry con pedido CONFIRMADO retorna 422

- **WHEN** un usuario autenticado realiza `POST /api/v1/pagos/crear` con un `pedido_id` cuyo estado es `CONFIRMADO` (o cualquier estado distinto de `PENDIENTE`)
- **THEN** el sistema retorna HTTP 422 indicando que el pedido no está disponible para pago

#### Scenario: Retry con último pago no rechazado retorna 422

- **WHEN** un usuario autenticado realiza `POST /api/v1/pagos/crear` con un `pedido_id` en estado `PENDIENTE` pero cuyo último pago tiene `mp_status` distinto de `"rejected"` (ej: `"approved"`, `"in_process"`)
- **THEN** el sistema retorna HTTP 422 indicando que ya existe un pago en curso o aprobado para este pedido

#### Scenario: Intentos previos preservados en BD

- **WHEN** se realiza un retry de pago sobre un pedido que ya tiene intentos previos
- **THEN** los registros de `Pago` anteriores permanecen intactos en la base de datos, cada uno con su propio `idempotency_key` y `external_reference` únicos
