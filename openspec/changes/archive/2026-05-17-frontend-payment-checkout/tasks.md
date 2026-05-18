## 1. Backend — Endpoint público formas de pago

- [x] 1.1 Crear `backend/pagos/router_publico.py` con endpoint `GET /` que retorna formas de pago activas
- [x] 1.2 Registrar el nuevo router en `backend/api/v1/router.py`

## 2. Frontend — Setup

- [x] 2.1 Instalar `@mercadopago/sdk-react` con pnpm
- [x] 2.2 Agregar `VITE_MP_PUBLIC_KEY` a `frontend/.env.example`
- [x] 2.3 Crear API layer para formas de pago en frontend
- [x] 2.4 Crear API layer para creación de pagos en frontend (`POST /api/v1/pagos/crear`)

## 3. Frontend — Checkout con selector de pago

- [x] 3.1 Agregar selector de forma de pago (radio buttons) en CheckoutPage
- [x] 3.2 Reemplazar forma_pago_codigo hardcodeado por el valor seleccionado
- [x] 3.3 Implementar flujo condicional: EFECTIVO/TRANSFERENCIA → crear pedido directo; MERCADOPAGO → crear pedido + mostrar tokenización

## 4. Frontend — Tokenización y pago

- [x] 4.1 Integrar `@mercadopago/sdk-react` con `VITE_MP_PUBLIC_KEY`
- [x] 4.2 Implementar formulario de tokenización de tarjeta post-creación de pedido
- [x] 4.3 Llamar a `POST /api/v1/pagos/crear` con card_token obtenido
- [x] 4.4 Usar paymentStore para trackear estado del pago (processing, approved, rejected, pending)

## 5. Frontend — Resultado del pago

- [x] 5.1 Modificar OrderConfirmation para mostrar badge de estado del pago
- [x] 5.2 Manejar reintento cuando el pago es rechazado
- [x] 5.3 Manejar error de red con opción de reintentar
- [x] 5.4 Manejar caso de pago pendiente
