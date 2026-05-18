## 1. Helper de consulta MercadoPago

- [ ] 1.1 Agregar función `consultar_pago_mp(mp_payment_id: int) -> dict` en `backend/pagos/mp_client.py`
- [ ] 1.2 Manejar errores de conexión/API del SDK dentro de la función

## 2. Modificar avanzar_estado() en pedidos

- [ ] 2.1 Modificar firma de `avanzar_estado()` para aceptar `usuario_actual: Usuario | None = None`
- [ ] 2.2 Implementar lógica de sistema: cuando `usuario_actual is None`, validar con rol SISTEMA y registrar usuario_id=NULL en historial

## 3. Service — Procesamiento de webhook

- [ ] 3.1 Crear función `validar_firma_webhook(raw_body: bytes, x_signature: str) -> bool` con HMAC-SHA256 y comparación constant-time
- [ ] 3.2 Crear función `procesar_webhook(uow, raw_body, x_signature) -> None` en service
- [ ] 3.3 Parsear payload IPN y extraer mp_payment_id
- [ ] 3.4 Consultar MP vía `consultar_pago_mp()` y actualizar Pago.mp_status
- [ ] 3.5 Implementar idempotencia: skip si Pago.mp_status ya coincide
- [ ] 3.6 Si status=approved: llamar `avanzar_estado()` para PENDIENTE→CONFIRMADO
- [ ] 3.7 Si status distinto: solo actualizar Pago, no avanzar pedido
- [ ] 3.8 Manejar casos edge: Pago no encontrado, pedido ya no PENDIENTE, error MP API

## 4. Router — Endpoint webhook

- [ ] 4.1 Crear endpoint `POST /webhook` en `backend/pagos/router.py` sin autenticación
- [ ] 4.2 Extraer raw body del request y header X-Signature
- [ ] 4.3 Si firma inválida → HTTP 401; si válida → procesar y 200
- [ ] 4.4 Registrar endpoint en API v1 (ya está en sub_routers el de pagos)

## 5. Tests

- [ ] 5.1 Escribir test de webhook con firma válida → 200
- [ ] 5.2 Escribir test de webhook con firma inválida → 401
- [ ] 5.3 Escribir test de pago aprobado → avanza pedido a CONFIRMADO
- [ ] 5.4 Escribir test de pago rechazado → pedido queda PENDIENTE
- [ ] 5.5 Escribir test de idempotencia: mismo estado → skip sin efectos
- [ ] 5.6 Escribir test de mp_payment_id no encontrado → 200 sin errores
