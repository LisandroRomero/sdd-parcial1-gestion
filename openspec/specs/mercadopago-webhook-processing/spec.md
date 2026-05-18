## ADDED Requirements

### Requirement: Recibir y validar webhook IPN de MercadoPago
El sistema SHALL exponer `POST /api/v1/pagos/webhook` como punto de entrada para notificaciones IPN de MercadoPago. El endpoint NO SHALL requerir autenticación. El sistema SHALL validar la firma `X-Signature` usando `MERCADOPAGO_WEBHOOK_SECRET`. Si la firma es inválida, SHALL responder HTTP 401.

#### Scenario: Webhook con firma válida
- **WHEN** el endpoint recibe un webhook con `X-Signature` válida según `MERCADOPAGO_WEBHOOK_SECRET`
- **THEN** el sistema procesa la notificación y responde HTTP 200

#### Scenario: Webhook con firma inválida
- **WHEN** el endpoint recibe un webhook con `X-Signature` inválida o ausente
- **THEN** el sistema responde HTTP 401 y no procesa la notificación

### Requirement: Procesar topic=payment
El sistema SHALL procesar notificaciones IPN con `topic=payment` o `type=payment`. SHALL obtener el `mp_payment_id` del payload, consultar el estado actual del pago en MercadoPago vía SDK, y actualizar `Pago.mp_status` en la base de datos.

#### Scenario: topic=payment con pago aprobado
- **WHEN** el webhook notifica un pago con `status=approved` en MercadoPago
- **THEN** el sistema actualiza `Pago.mp_status` a `"approved"` en la base de datos

#### Scenario: topic=payment con pago rechazado
- **WHEN** el webhook notifica un pago con `status=rejected` en MercadoPago
- **THEN** el sistema actualiza `Pago.mp_status` a `"rejected"` en la base de datos

#### Scenario: mp_payment_id no encontrado en BD
- **WHEN** el `mp_payment_id` del webhook no existe en la tabla `Pago`
- **THEN** el sistema ignora la notificación y responde HTTP 200

#### Scenario: Error de conexión con MercadoPago
- **WHEN** ocurre un error de conexión al consultar MercadoPago vía SDK
- **THEN** el sistema loguea el error y responde HTTP 200

### Requirement: Avanzar pedido al confirmar pago
El sistema SHALL avanzar automáticamente el pedido de `PENDIENTE` a `CONFIRMADO` cuando el pago es aprobado, utilizando el service de pedidos (`avanzar_estado`). El historial SHALL registrar `usuario_id=NULL` indicando transición del sistema. El descuento de stock SHALL ocurrir como parte de la transición a CONFIRMADO.

#### Scenario: Pago aprobado → pedido avanza
- **WHEN** el webhook notifica un pago aprobado y el pedido asociado está en estado `PENDIENTE`
- **THEN** el sistema avanza el pedido a `CONFIRMADO` mediante `avanzar_estado`, registra `usuario_id=NULL` en el historial, y el stock se descuenta

#### Scenario: Pago rechazado → pedido no avanza
- **WHEN** el webhook notifica un pago rechazado
- **THEN** el sistema actualiza `Pago.mp_status` a `"rejected"` pero el pedido permanece en `PENDIENTE` y no se descuenta stock

#### Scenario: Pedido ya no está PENDIENTE
- **WHEN** el webhook notifica un pago aprobado pero el pedido ya no está en `PENDIENTE` (ej: cancelado manualmente)
- **THEN** el sistema actualiza `Pago.mp_status` sin lanzar error ni modificar el estado del pedido

### Requirement: Idempotencia en webhook
El sistema SHALL ser idempotente frente a webhooks duplicados. Si ya se procesó un `mp_payment_id` con el mismo estado, SHALL ignorar la notificación sin efectos secundarios.

#### Scenario: Webhook duplicado con mismo estado
- **WHEN** el sistema recibe un webhook para un `mp_payment_id` cuyo `mp_status` ya coincide con el estado notificado
- **THEN** el sistema ignora la notificación, no reprocesa, y responde HTTP 200

#### Scenario: Webhook duplicado con estado diferente
- **WHEN** el sistema recibe un webhook para un `mp_payment_id` cuyo `mp_status` es diferente al estado notificado
- **THEN** el sistema actualiza `Pago.mp_status` con el nuevo estado y ejecuta las acciones correspondientes (avanzar pedido si aplica)
