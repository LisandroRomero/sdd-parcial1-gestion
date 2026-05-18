## Why

El módulo `backend/pagos/` tiene el modelo de datos completo (`Pago`, `FormaPago`) y las tablas creadas en BD, pero **carece de toda lógica de negocio**: no hay service, repository, router, ni integración con el SDK de MercadoPago. Sin este cambio, ningún cliente puede pagar un pedido a través de la plataforma.

Este cambio implementa el endpoint `POST /api/v1/pagos/crear` que permite a un cliente autenticado crear un pago en MercadoPago usando el token de tarjeta generado por el frontend (SDK de MercadoPago del lado del cliente), registrando la transacción en la tabla `Pago` de forma atómica vía UoW.

## What Changes

- **`PagoService.crear_pago()`** — lógica de negocio para crear un pago en MercadoPago:
  - Validar que el pedido pertenezca al cliente autenticado
  - Validar que el pedido esté en estado `PENDIENTE`
  - Generar `idempotency_key` UUID para evitar cobros duplicados
  - Llamar a la API de MercadoPago vía SDK (`mercadopago` Python) con `card_token`, `payment_method_id`, `transaction_amount`, `external_reference` (UUID del pedido), `description`, e `idempotency_key`
  - Registrar el `Pago` en BD con `mp_payment_id`, `mp_status`, y datos de la transacción atómicamente vía UoW
  - Retornar el resultado del pago al frontend

- **`PagoRepository`** — hereda de `BaseRepository[Pago]` con métodos específicos:
  - `get_by_pedido(pedido_id)` — obtener pagos de un pedido
  - `get_by_mp_payment_id(mp_payment_id)` — búsqueda por ID de MP
  - `get_by_idempotency_key(key)` — verificar duplicados por idempotency key

- **`POST /api/v1/pagos/crear`** — nuevo endpoint REST:
  - Recibe `CrearPagoRequest` con `pedido_id`, `card_token`, `payment_method_id`
  - Requiere autenticación (`CLIENT` o `ADMIN`)
  - Retorna `PagoResponse` con `mp_payment_id`, `mp_status`, `id` del Pago registrado

- **Schemas Pydantic actualizados:**
  - `CrearPagoRequest` con `pedido_id: int`, `card_token: str`, `payment_method_id: str`, `monto: Decimal`
  - `PagoResponse` con datos completos del pago creado
  - `PagoRead` ajustado según el modelo actual

- **Config extendida:**
  - Agregar `MP_PUBLIC_KEY` (para frontend) y `MP_NOTIFICATION_URL` a `Settings`

- **Router registrado** en `backend/api/v1/router.py` bajo prefijo `/pagos`

- **Cliente SDK de MercadoPago** inicializado como singleton/dependencia con `MERCADOPAGO_ACCESS_TOKEN`

## Capabilities

### New Capabilities
- `mercadopago-payment-creation`: Capacidad para crear pagos en MercadoPago desde el backend, incluyendo validación de pedido, generación de idempotency key, comunicación con la API de MP vía SDK, y registro atómico del pago en la base de datos.

### Modified Capabilities
- `admin-payment-settings`: El toggle de formas de pago (`activo`) debería afectar qué métodos de pago están disponibles al crear un pago. Este cambio no modifica la spec actual, pero el `PagoService` deberá verificar `FormaPago.activo = true` al validar el `payment_method_id`.

## Impact

- **Backend** (`backend/pagos/`): implementar `repository.py`, `service.py`, `router.py` desde cero; actualizar `schemas.py`
- **Backend** (`backend/core/config.py`): agregar `MP_PUBLIC_KEY` y `MP_NOTIFICATION_URL`
- **Backend** (`backend/api/v1/router.py`): registrar `pagos_router`
- **Infra**: requiere `MERCADOPAGO_ACCESS_TOKEN` configurado en el entorno (ya está en `.env.example`)
- **Sin impacto en frontend**: este cambio es puramente backend; la integración frontend es el change 6.4
- **Sin impacto en pedidos**: la FSM del pedido NO cambia; el pago se registra pero el pedido sigue `PENDIENTE` hasta que el webhook (6.2) lo confirme
