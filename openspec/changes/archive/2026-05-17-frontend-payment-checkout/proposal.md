## Why

El checkout actual crea pedidos con `forma_pago_codigo: 'EFECTIVO'` hardcodeado, sin ofrecer al cliente la posibilidad de pagar con MercadoPago. Con el backend de pagos ya implementado (change `mercadopago-payment-creation`), el frontend debe exponer un selector de método de pago y, para MercadoPago, tokenizar la tarjeta vía SDK del lado del cliente y enviar el pago al backend.

## What Changes

- **`Frontend`**: Instalar `@mercadopago/sdk-react` como dependencia
- **`Frontend`**: Agregar `VITE_MP_PUBLIC_KEY` al archivo `frontend/.env.example`
- **`Backend`**: Crear endpoint público `GET /api/v1/pagos/formas-pago` que retorna las formas de pago con `activo = true` (`FormaPagoRead`)
- **`CheckoutPage.tsx`**: Agregar selector de forma de pago (radio buttons) que carga las formas activas desde el nuevo endpoint
- **`CheckoutPage.tsx`**: Para MercadoPago, integrar formulario de tokenización de tarjeta vía `@mercadopago/sdk-react` (`CardPayment` o `usePaymentForm`)
- **`CheckoutPage.tsx`**: Modificar flujo de envío: si la forma seleccionada es EFECTIVO o TRANSFERENCIA, crear pedido sin pago; si es MERCADOPAGO, crear pedido → tokenizar tarjeta → `POST /api/v1/pagos/crear` → mostrar resultado
- **`OrderConfirmation`**: Mostrar resultado del pago (aprobado/rechazado/pendiente) según la respuesta del backend
- **`paymentStore`** (Zustand existente): Almacenar estado del pago actual en el flujo de checkout
- **`Rutas`**: Registrar `formas_pago_router` (backend) en `backend/api/v1/router.py`

## Capabilities

### New Capabilities

- `payment-checkout-frontend`: Capacidad para que el frontend de checkout seleccione métodos de pago (EFECTIVO, TRANSFERENCIA, MERCADOPAGO), tokenice tarjetas vía SDK de MercadoPago, cree pedidos con la forma de pago elegida, y ejecute el pago contra `POST /api/v1/pagos/crear` mostrando el resultado al cliente.

### Modified Capabilities

*Ninguna.*

## Impact

- **Backend** (`backend/pagos/`): agregar `router_publico.py` con `GET /api/v1/pagos/formas-pago`
- **Backend** (`backend/api/v1/router.py`): registrar `formas_pago_router`
- **Frontend**: instalar `@mercadopago/sdk-react`
- **Frontend** (`frontend/.env.example`): agregar `VITE_MP_PUBLIC_KEY`
- **Frontend** (`frontend/src/pages/checkout/CheckoutPage.tsx`): overhaul del formulario de checkout
- **Frontend** (`frontend/src/pages/checkout/OrderConfirmation.tsx`): nuevo componente o modificación para mostrar estado del pago
- **Frontend** (`frontend/src/features/payment/store/paymentStore.ts`): usar store existente para estado de pago durante el flujo
