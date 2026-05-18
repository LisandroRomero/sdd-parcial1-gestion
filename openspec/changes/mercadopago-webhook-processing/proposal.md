## Why

El endpoint `POST /api/v1/pagos/crear` (change 6.1) ya genera pagos en MercadoPago, pero el sistema no puede procesar las notificaciones asincrónicas (IPN) que envía MP cuando un pago cambia de estado. Sin este change, los pagos aprobados nunca avanzan el pedido de `PENDIENTE` a `CONFIRMADO`, rompiendo el flujo completo del e-commerce.

## What Changes

1. Nuevo endpoint `POST /api/v1/pagos/webhook` como punto de entrada para IPN de MercadoPago, sin autenticación, con validación de firma `X-Signature`
2. Procesamiento de `topic=payment`: consultar estado actual del pago en MP vía SDK, actualizar `Pago.mp_status` en BD
3. Si el pago fue aprobado (`status=approved`): avanzar el pedido de `PENDIENTE` a `CONFIRMADO` vía el service de pedidos (`avanzar_estado`), registrando en `HistorialEstadoPedido` con `usuario_id=NULL`
4. Si el pago fue rechazado: solo actualizar `Pago.mp_status`, el pedido permanece `PENDIENTE`
5. Idempotencia: no reprocesar si `mp_payment_id` ya fue procesado (safe retry)
6. Config `MERCADOPAGO_WEBHOOK_SECRET` ya presente en `config.py`

## Capabilities

### New Capabilities

- `mercadopago-webhook-processing`: Procesa notificaciones IPN de MercadoPago (`topic=payment`), actualiza el estado del pago en BD y, si corresponde, avanza automáticamente el estado del pedido en la FSM registrando la transición como origen-sistema (`usuario_id=NULL`)

### Modified Capabilities

Ninguna. La spec `order-state-machine` ya contempla el escenario "Transición del sistema registra NULL" con `usuario_id=NULL`. Este change es la primera implementación concreta que dispara ese escenario, pero no modifica sus requirements.

## Impact

- `backend/pagos/router.py` — nuevo endpoint `POST /api/v1/pagos/webhook`
- `backend/pagos/service.py` — nuevo método `procesar_webhook()`
- `backend/pagos/schemas.py` — nuevos schemas para request/response del webhook
- `backend/pagos/mp_client.py` — extender con método para consultar estado de pago por ID
- `backend/pedidos/service.py` — consumir `avanzar_estado` para PENDIENTE → CONFIRMADO
- `openspec/specs/mercadopago-webhook-processing/spec.md` — nueva spec
- Dependencias: changes 0.4, 1.5, 5.1, 5.2, 6.1 (todos archivados)
