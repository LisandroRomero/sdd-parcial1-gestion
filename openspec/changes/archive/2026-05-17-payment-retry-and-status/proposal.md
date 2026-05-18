## Why

Currently, a pedido can only have a single payment record due to the unique constraint on `external_reference` (set to `str(pedido.id)`). When a payment is rejected, the customer cannot retry — they would need to create a new order. Additionally, there is no endpoint to query the payment status of an order, forcing the client to guess or rely on webhook timing. This blocks US-047 (consultar estado de pago) and US-048 (reintentar pago rechazado).

## What Changes

- **New endpoint** `GET /api/v1/pagos/{pedido_id}` returns all payment attempts for an order with their statuses
- **Retry support** in `POST /api/v1/pagos/crear`: when called for a pedido with a rejected previous attempt, it generates a new `idempotency_key` and a unique `external_reference` (appending attempt counter) so the second payment does not violate the unique constraint
- **1:N payment-to-order enforcement**: the existing model already allows this (no unique on `pedido_id`); the creation logic will be updated to generate unique `external_reference` per attempt instead of reusing `str(pedido.id)`
- The pedido must remain in `PENDIENTE` state to allow retries (already enforced by RN-PA06)
- All previous payment attempts remain visible in the payment history for audit

## Capabilities

### New Capabilities

- `payment-status-query`: Expose `GET /api/v1/pagos/{pedido_id}` returning all payment attempts for an order with status, amount, and timestamps. Must enforce ownership (client sees own orders only; admin sees all).
- `payment-retry`: Allow retrying a rejected payment on the same pedido by generating a fresh `idempotency_key` and unique `external_reference`. Preserves all prior attempt records. Requires pedido in `PENDIENTE` state.

### Modified Capabilities

- `mercadopago-payment-creation`: The `external_reference` generation requirement changes from `str(pedido.id)` (unique per pedido, blocking retries) to a pedido-scoped unique value (e.g., `str(pedido.id) + "-" + attempt_number`). The creation endpoint must also validate that retries are allowed (pedido is PENDIENTE, previous payment was rejected).

## Impact

- **Backend/pagos**: `service.py` needs retry logic and a new method for status query; `repository.py` needs `find_by_pedido_id`; `router.py` adds `GET /api/v1/pagos/{pedido_id}`; `schemas.py` may need a response type for multi-attempt status
- **Backend/pedidos**: no state machine changes — pedido stays `PENDIENTE` on rejection (already enforced)
- **Model**: no DDL changes — `Pago` already supports 1:N; only `external_reference` generation logic changes at the application layer
- **IDempotency**: `idempotency_key` unique constraint remains correct — each retry generates a fresh UUID
