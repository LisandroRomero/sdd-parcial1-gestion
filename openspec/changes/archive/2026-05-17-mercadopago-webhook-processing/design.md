## Context

Food Store generates payments via `POST /api/v1/pagos/crear` (change 6.1) and delegates async status updates to MercadoPago IPN webhooks. Currently the system has no endpoint to receive those webhooks, so approved payments never trigger the PENDIENTE → CONFIRMADO transition in the order FSM.

Existing infrastructure:
- `backend/pagos/` — Pago model (with `mp_payment_id`, `mp_status`), repository (with `get_by_mp_payment_id`, `get_by_idempotency_key`), service (`crear_pago`), router.
- `backend/pedidos/service.py` — `avanzar_estado()` implements the FSM transition with role validation. The map already defines `"PENDIENTE" → "CONFIRMADO"` with `"SISTEMA"` role for webhook-origin transitions.
- `backend/core/config.py` — `mercadopago_webhook_secret` already present.
- `backend/core/uow.py` — UnitOfWork with commit/rollback, per-request session lifecycle.

## Goals / Non-Goals

**Goals:**
- Process MercadoPago IPN webhooks for `topic=payment` / `action=payment.created`
- Validate incoming webhook authenticity via `X-Signature` HMAC-SHA256
- Update `Pago.mp_status` from the MP API response when notified
- Advance order from PENDIENTE → CONFIRMADO when MP returns `status=approved`
- Ensure idempotency: safe retry without duplicate processing
- Record all system-originated transitions with `usuario_id=NULL` in `HistorialEstadoPedido`

**Non-Goals:**
- Processing IPN topics other than `payment` (e.g. `merchant_order`) — out of scope for this change
- Retry logic for failed webhook processing (MP handles retries; we just need to be idempotent)
- Refactoring the existing `avanzar_estado()` signature beyond making `usuario_actual` optional
- Rate limiting or abuse prevention on the webhook endpoint (MP IPs are dynamic)
- Manual reconciliation dashboard — this is purely async processing

## Decisions

### 1. Signature validation in the endpoint handler, not middleware

**Decision:** Validate `X-Signature` HMAC-SHA256 inside the webhook endpoint handler itself.

**Rationale:** There is only one webhook endpoint in the system. A middleware would need route exclusion logic for all other paths, adding complexity for no benefit. The endpoint handler is simpler, self-contained, and fails fast with a clear 401.

**Implementation:** Compute HMAC-SHA256 of the raw request body using `mercadopago_webhook_secret` and compare (constant-time) against the `X-Signature` header. If mismatch → return `HTTP 401`.

**Trade-off:** The raw body must be read before Pydantic parsing. We'll use `request.body()` and pass bytes to the validation function, then parse the JSON after validation passes.

### 2. Query MP status via existing SDK

**Decision:** Use the existing `get_mp_client()` factory and call `payment().get(mp_payment_id)` to obtain current payment status from MercadoPago.

**Rationale:** The SDK is already initialized, cached, and configured with `mercadopago_access_token`. It's used in `crear_pago()` for payment creation — using it for status queries is consistent and avoids a second HTTP client.

**Implementation:** Add a helper function in `mp_client.py`:
```python
def consultar_pago_mp(mp_payment_id: int) -> dict:
    client = get_mp_client()
    result = client.payment().get(mp_payment_id)
    return result.get("response", {})
```

### 3. Consume `avanzar_estado()` from pedidos service after making `usuario_actual` optional

**Decision:** Modify `avanzar_estado()` in `pedidos/service.py` to accept an optional `usuario_actual` parameter. When `None`, validate using the `"SISTEMA"` role and record `usuario_id=NULL` in `HistorialEstadoPedido`.

**Rationale:** The FSM map already defines `"SISTEMA"` as a valid role for PENDIENTE → CONFIRMADO. Adding a parallel method would duplicate the FSM logic. Making the parameter optional with a `None = system` convention is the minimal, backward-compatible change. Existing callers (admin panel) continue passing a `Usuario` as before.

**Signature change:**
```python
def avanzar_estado(
    uow: UnitOfWork,
    pedido_id: int,
    nuevo_estado: str,
    usuario_actual: Usuario | None = None,
) -> Pedido:
```

When `usuario_actual is None`:
- Use `{"SISTEMA"}` as the roles set for transition validation
- Set `usuario_id=None` in `HistorialEstadoPedido`

### 4. Idempotency by comparing current `mp_status`

**Decision:** Before processing a webhook notification, fetch the `Pago` record by `mp_payment_id`. If `pago.mp_status` already matches the status from MP API, skip the update and return early.

**Rationale:** MercadoPago may resend the same webhook multiple times (at-least-once delivery). The most reliable idempotency key is the current `mp_status` itself — if it already reflects the notified status, there's nothing to do.

**Implementation:**
```python
pago = uow.repos.pagos.get_by_mp_payment_id(mp_payment_id)
if pago is None:
    return  # Unknown payment, nothing to do (return 200)

mp_status = mp_response.get("status")
if pago.mp_status == mp_status:
    return  # Already processed this status, idempotent skip
```

### 5. Error handling: return 200 for all non-recoverable scenarios

**Decision:** The webhook endpoint always returns HTTP 200 to MercadoPago, even on processing failures, except for signature validation errors (401).

**Rationale:** MercadoPago retries webhooks on non-200 responses. Most "failures" in our processing are not recoverable by retry:
- Unknown `mp_payment_id` → MP retrying won't make the record appear
- MP API down → our issue, not something a retry from MP will fix
- Order already advanced → returning non-200 would cause unnecessary retries of an already-processed notification
- Transition validation error → pedido is in a state that can't advance (e.g. already CONFIRMADO or CANCELADO)

**Exceptions:**
- `X-Signature` mismatch → `HTTP 401` (security-critical, do not mask)
- Network/parse errors log and return 200 (avoid retry storms)

**Transaction atomicity:** All DB writes (mp_status update + order state transition) happen within a single UoW. If the order transition fails (e.g. validation error), the entire UoW rolls back, including the mp_status update. This prevents a partial state where Pago is "approved" but the order remains "PENDIENTE".

## Risks / Trade-offs

1. **Modifying `avanzar_estado()` signature** — existing callers in `admin/` and future features depend on the current signature. Making `usuario_actual` optional (`Usuario | None = None`) is backward compatible but introduces branching logic (null vs non-null). Mitigation: add a `# system transition` guard clause with a clear docstring.

2. **No inbound IP allowlist for MP** — MercadoPago does not publish a static IP range for webhooks. We rely solely on `X-Signature` validation. Risk: if the secret is leaked, an attacker could forge webhooks. Mitigation: the secret is env-configurable and should be managed as a production secret.

3. **Race condition on concurrent webhooks** — MP could send two webhooks for the same payment simultaneously (e.g. `payment.created` and `payment.updated` in quick succession). The UoW serializes writes, and the idempotency check guards against double-processing, but in theory a race could sneak past the status check. Mitigation: low probability (MP sends one notification per status change); the worst case is an unnecessary `avanzar_estado()` call that fails harmlessly with ConflictException.

4. **MP API latency** — `payment().get()` adds an outbound HTTP call on the webhook critical path. If MP API is slow, the endpoint could timeout before returning 200, triggering MP retries. Mitigation: no mitigation in this change — the impact is limited (retried notifications) and MP API latency is typically sub-second.
