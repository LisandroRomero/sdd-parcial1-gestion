## Context

The checkout page at `frontend/src/pages/checkout/CheckoutPage.tsx` currently:

- Has a 2-column layout: left = `CheckoutSummary`, right = `AddressSelector` + total + "Confirmar pedido" button
- Hardcodes `forma_pago_codigo: 'EFECTIVO'` when creating the order
- Has 3 states: idle (form), pending (spinner), success (`OrderConfirmation`)
- Error handling: 401/403 → `NoPermissionMessage`, others → `ErrorMessage` + retry, offline → `OfflineMessage`

`OrderConfirmation.tsx` shows a green checkmark, `#pedidoId`, total, and links to order detail and catalog — no payment logic.

A `paymentStore` (`frontend/src/shared/lib/stores/payment.store.ts`) already exists with Zustand, including `PaymentStatus` type (`idle | processing | approved | rejected | pending`) and actions.

The backend pagos module already has:
- `POST /api/v1/pagos/crear` — needs `pedido_id`, `card_token`, `payment_method_id`, `monto`
- `FormaPago` model with `activo` flag
- `get_mp_client()` singleton via `@lru_cache`
- `MP_PUBLIC_KEY` configured via settings

Seed data has 3 formas de pago: MERCADOPAGO (activo), EFECTIVO (activo), TRANSFERENCIA (activo).

## Goals / Non-Goals

**Goals:**
- Add a payment method selector (radio buttons / visual cards) to the checkout form, loading active payment methods dynamically
- For EFECTIVO / TRANSFERENCIA: submit order directly without payment (existing flow)
- For MERCADOPAGO: create order → tokenize card via MercadoPago SDK → POST to `/api/v1/pagos/crear` → display result (approved / rejected / pending)
- Install `@mercadopago/sdk-react` for frontend card tokenization (PCI-compliant)
- Create backend endpoint `GET /api/v1/pagos/formas-pago` returning active payment methods only
- Expose `VITE_MP_PUBLIC_KEY` in the frontend environment
- Show payment result in `OrderConfirmation` (approved badge, rejected error with retry, pending message)
- Use existing `paymentStore` to track payment state during the checkout flow

**Non-Goals:**
- ❌ Processing webhooks IPN from MercadoPago (change `mercadopago-webhook-processing`)
- ❌ Payment retry logic or multiple payments per order
- ❌ Offline payment methods (Rapipago / Pago Fácil)
- ❌ Saved cards or customer payment profiles
- ❌ Refunds or partial payments

## Decisions

### 1. Load payment methods from dynamic endpoint, not hardcoded

**Decision:** Create `GET /api/v1/pagos/formas-pago` (public, no auth required) and fetch the list on checkout mount. Render radio buttons or visual cards for each active form of payment.

**Alternativa considerada:** Hardcode the 3 seed payment methods (`EFECTIVO`, `TRANSFERENCIA`, `MERCADOPAGO`) directly in the frontend.

**Razón:** The admin panel has the ability to toggle `FormaPago.activo`. A hardcoded list would require a frontend deploy to reflect those changes. Loading dynamically means the toggle takes effect immediately. The cost of one extra `GET` request on the checkout page is negligible.

### 2. Inline payment flow (same page), not redirect to separate page

**Decision:** Keep the entire payment flow on the checkout page. After the user confirms:
- If EFECTIVO or TRANSFERENCIA: create order directly (existing behavior).
- If MERCADOPAGO: create order → on success, render card tokenization form inline → tokenize via SDK → `POST /api/v1/pagos/crear` → render result in `OrderConfirmation`.

**Alternativa considerada:** Redirect to a dedicated `/pago/:pedidoId` page for MercadoPago payment.

**Razón:** A redirect adds page load time and context switch. Keeping the flow inline avoids losing the user's place, simplifies state management (no need to pass `pedidoId` across routes), and the `paymentStore` already lives in the client. The checkout page already manages a multi-step UI (idle → pending → success), so adding one more step (tokenization sub-form) is a natural extension.

### 3. Use `@mercadopago/sdk-react` for card tokenization, not a custom form

**Decision:** Install `@mercadopago/sdk-react` and use its `<CardPayment />` component or `usePaymentForm` hook to tokenize the card. The token is then sent to `POST /api/v1/pagos/crear`.

**Alternativa considerada:** Build a custom card form and use the MercadoPago raw JavaScript SDK.

**Razón:** PCI-DSS compliance. MercadoPago's SDK handles card data collection in a secured iframe, so the raw card number, CVV, and expiry never reach the frontend application's memory or network. A custom form would touch raw PAN data, requiring PCI SAQ-D certification. Using the React SDK keeps the frontend out of scope for PCI audit and is the recommended integration path per MercadoPago documentation.

### 4. `VITE_MP_PUBLIC_KEY` in frontend env (client-side safe)

**Decision:** Add `VITE_MP_PUBLIC_KEY` to `frontend/.env.example`. The frontend reads it at build time via `import.meta.env.VITE_MP_PUBLIC_KEY` and passes it to `initMercadoPago()`.

**Alternativa considerada:** Serve the public key from a backend endpoint (`GET /api/v1/pagos/public-key`).

**Razón:** The public key is not secret. It's designed to be embedded in client-side code (MercadoPago documentation explicitly instructs including it in the frontend bundle). Serving it from a backend endpoint adds an extra request and unnecessary complexity. `VITE_` prefix ensures Vite inlines it at build time. The backend `MP_PUBLIC_KEY` env var is already configured; the frontend simply needs a matching `VITE_MP_PUBLIC_KEY` in its own `.env`.

### 5. Payment result in OrderConfirmation + paymentStore

**Decision:** `OrderConfirmation` receives payment data as optional props. When present, it shows:
- `approved` → green badge "Pago aprobado" + existing confirmation
- `rejected` → red error + "Reintentar con otra tarjeta" button
- `pending` → yellow/orange badge "Pago en proceso"

The `paymentStore` tracks the `PaymentStatus` and holds the `paymentId` and `error`. It is reset when leaving checkout.

**Alternativa considerada:** Create a separate `PaymentResult` component and conditionally render it.

**Razón:** `OrderConfirmation` is already the success state of checkout. Adding optional payment info avoids introducing a new component for what is essentially the same screen. The `paymentStore` is already designed for this use case — no new store is needed. Zustand ensures type-safe access across the checkout lifecycle.

### 6. `GET /api/v1/pagos/formas-pago` as a public endpoint

**Decision:** Create a new module `backend/pagos/router_publico.py` with `GET /api/v1/pagos/formas-pago` returning `list[FormaPagoRead]` for records where `activo = true`. Register it in `backend/api/v1/router.py` with no authentication dependency.

**Alternativa considerada:** Serve the endpoint under the existing `pagos_router` with optional auth.

**Razón:** Payment methods must be visible to unauthenticated users (e.g., before login / during guest browsing). Separating public routes into `router_publico.py` keeps a clear security boundary and follows the principle of least privilege. If auth is desired later, it can be added to this specific router without touching the authenticated payment creation endpoints.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| MercadoPago SDK initialization fails (bad public key, CDN blocked) | Payment form not rendered; user cannot pay with card | Graceful fallback: hide card form, show "Medio no disponible" and suggest EFECTIVO / TRANSFERENCIA |
| Network loss after `POST /api/v1/pagos/crear` but before receiving response | User sees error but payment may have been created | The backend `POST /pagos/crear` is idempotent via `idempotency_key`. Frontend can offer "Verificar estado" button that queries the pedido's payment status |
| User refreshes the page during card tokenization | Loses card form state but pedido already exists | On mount, if paymentStore has `status: 'pending'` and there is a `pedidoId`, show resume UI instead of starting over |
| `VITE_MP_PUBLIC_KEY` is missing / empty string | SDK initialization fails silently | Validate env var before `initMercadoPago()` and show configuration error in dev mode; hide MP option in production |
| Token expires while user is filling card form | MP SDK shows its own timeout error | The SDK handles token lifecycle. On 400 from `/pagos/crear` due to expired token, show error and allow user to re-enter card details |
