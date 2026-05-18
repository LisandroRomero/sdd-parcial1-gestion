## 1. Backend — Endpoint público formas de pago

- [ ] 1.1 Crear `backend/pagos/router_publico.py` con endpoint `GET /` que retorna formas de pago activas
- [ ] 1.2 Registrar el nuevo router en `backend/api/v1/router.py`

## 2. Frontend — Setup

- [ ] 2.1 Instalar `@mercadopago/sdk-react` con pnpm
- [ ] 2.2 Agregar `VITE_MP_PUBLIC_KEY` a `frontend/.env.example`
- [ ] 2.3 Crear API layer para formas de pago en frontend
- [ ] 2.4 Crear API layer para creación de pagos en frontend (`POST /api/v1/pagos/crear`)

## 3. Frontend — Checkout con selector de pago

- [ ] 3.1 Agregar selector de forma de pago (radio buttons) en CheckoutPage
- [ ] 3.2 Reemplazar forma_pago_codigo hardcodeado por el valor seleccionado
- [ ] 3.3 Implementar flujo condicional: EFECTIVO/TRANSFERENCIA → crear pedido directo; MERCADOPAGO → crear pedido + mostrar tokenización

## 4. Frontend — Tokenización y pago

- [ ] 4.1 Integrar `@mercadopago/sdk-react` con `VITE_MP_PUBLIC_KEY`
- [ ] 4.2 Implementar formulario de tokenización de tarjeta post-creación de pedido
- [ ] 4.3 Llamar a `POST /api/v1/pagos/crear` con card_token obtenido
- [ ] 4.4 Usar paymentStore para trackear estado del pago (processing, approved, rejected, pending)

## 5. Frontend — Resultado del pago

- [ ] 5.1 Modificar OrderConfirmation para mostrar badge de estado del pago
- [ ] 5.2 Manejar reintento cuando el pago es rechazado
- [ ] 5.3 Manejar error de red con opción de reintentar
- [ ] 5.4 Manejar caso de pago pendiente
