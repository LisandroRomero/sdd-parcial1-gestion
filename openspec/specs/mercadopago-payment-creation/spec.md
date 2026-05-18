## ADDED Requirements

### Requirement: Crear pago en MercadoPago desde backend

El sistema SHALL proveer `POST /api/v1/pagos/crear` accesible para usuarios autenticados con rol CLIENT o ADMIN, que reciba un token de tarjeta y cree un pago en MercadoPago, registrando la transacción en la tabla `Pago` de forma atómica.

#### Scenario: Pago creado exitosamente con tarjeta aprobada

- **WHEN** un usuario CLIENT autenticado realiza `POST /api/v1/pagos/crear` con `pedido_id`, `card_token`, `payment_method_id` válidos, y el pedido está en estado `PENDIENTE` y le pertenece
- **THEN** el sistema genera un UUID como `idempotency_key`, llama a la API de MercadoPago con el SDK, recibe `mp_payment_id` y `status: "approved"`, registra el `Pago` en BD atómicamente vía UoW con esos datos, y retorna HTTP 201 con `PagoResponse` incluyendo `mp_payment_id`, `mp_status: "approved"`, y el `id` del registro

#### Scenario: Pago creado con tarjeta rechazada

- **WHEN** MercadoPago retorna `status: "rejected"` con un `status_detail` específico
- **THEN** el sistema registra el `Pago` en BD con `mp_status: "rejected"` y `status_detail`, el pedido permanece en `PENDIENTE`, y el endpoint retorna HTTP 201 con el estado `rejected` para que el frontend muestre el mensaje de error al cliente

#### Scenario: Pedido no encontrado retorna 404

- **WHEN** un usuario autenticado realiza `POST /api/v1/pagos/crear` con un `pedido_id` que no existe
- **THEN** el sistema retorna HTTP 404 Not Found

#### Scenario: Pedido no pertenece al usuario retorna 404

- **WHEN** un usuario CLIENT realiza `POST /api/v1/pagos/crear` con un `pedido_id` de un pedido que no le pertenece
- **THEN** el sistema retorna HTTP 404 Not Found (no revelar existencia del pedido)

#### Scenario: Pedido no está en estado PENDIENTE retorna 422

- **WHEN** un usuario autenticado realiza `POST /api/v1/pagos/crear` con un `pedido_id` cuyo estado no es `PENDIENTE`
- **THEN** el sistema retorna HTTP 422 con un mensaje indicando que el pedido no está disponible para pago

#### Scenario: Idempotency key duplicada no crea pago duplicado

- **WHEN** el sistema detecta que ya existe un `Pago` con la misma `idempotency_key` (por un reintento del frontend con la misma key)
- **THEN** el sistema retorna HTTP 409 Conflict indicando que ya existe un pago con esa key, y no se realiza ninguna llamada a MercadoPago

#### Scenario: Token de tarjeta inválido retorna error de MercadoPago

- **WHEN** MercadoPago rechaza la solicitud por `card_token` inválido o expirado
- **THEN** el sistema retorna HTTP 422 con el mensaje de error de MP para que el frontend solicite un nuevo token

#### Scenario: Forma de pago inactiva retorna 422

- **WHEN** el `payment_method_id` corresponde a una forma de pago con `activo = false`
- **THEN** el sistema retorna HTTP 422 indicando que la forma de pago no está disponible

#### Scenario: Usuario no autenticado retorna 401

- **WHEN** un request no autenticado realiza `POST /api/v1/pagos/crear`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Usuario sin rol CLIENT retorna 403

- **WHEN** un usuario autenticado con rol distinto a CLIENT (ej: STOCK, PEDIDOS) realiza `POST /api/v1/pagos/crear`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: Validar pertenencia del pedido al usuario

El sistema SHALL verificar que el pedido pertenezca al usuario autenticado antes de crear el pago. Si el usuario es ADMIN, SHALL permitir crear pagos para cualquier pedido.

#### Scenario: ADMIN crea pago para pedido de otro usuario

- **WHEN** un usuario ADMIN realiza `POST /api/v1/pagos/crear` con un `pedido_id` de otro usuario
- **THEN** el sistema permite la operación y retorna HTTP 201

### Requirement: Registrar pago en BD con datos completos

El sistema SHALL registrar cada intento de pago en la tabla `Pago` con los siguientes campos: `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference` (UUID del pedido), `idempotency_key`, `monto`, y `moneda`.

#### Scenario: Pago registrado con todos los campos requeridos

- **WHEN** se crea un pago exitosamente
- **THEN** la tabla `Pago` contiene un registro con `pedido_id`, `mp_payment_id no nulo`, `mp_status`, `external_reference = UUID del pedido`, `idempotency_key = UUID generado`, `monto` y `moneda`, y `created_at` con timestamp actual

### Requirement: Inicializar SDK de MercadoPago con access token

El sistema SHALL inicializar el SDK `mercadopago` con el `MERCADOPAGO_ACCESS_TOKEN` configurado en las variables de entorno.

#### Scenario: SDK configurado correctamente

- **WHEN** el sistema inicia y se importa el módulo de pagos
- **THEN** el SDK de MercadoPago se inicializa con el token de acceso configurado

#### Scenario: SDK no disponible retorna error 503

- **WHEN** el SDK de MercadoPago no puede inicializarse por token inválido o error de conexión
- **THEN** el sistema retorna HTTP 503 Service Unavailable
