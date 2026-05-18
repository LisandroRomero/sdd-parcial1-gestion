## Context

The platform supports single payment attempts per pedido via POST /api/v1/pagos/crear. There is no way for clients to query payment status of an order (they must rely on webhook timing), and rejected payments cannot be retried — the customer must create a new order. This design enables US-047 (payment status query) and US-048 (retry rejected payment).

**Current constraints:**
- Pago model already supports 1:N to Pedido (no unique on `pedido_id`) — no DDL changes needed
- `external_reference` is set to `str(pedido.id)`, which is identical across attempts → unique constraint violation on retry
- `idempotency_key` is a fresh UUID per call — already correct for retries
- Pedido stays PENDIENTE on payment rejection — state machine already allows retry
- `PagoRead` schema exists with `updated_at` field for status queries
- `get_by_pedido()` repository method exists and returns `list[Pago]` ordered by `created_at DESC`

## Goals / Non-Goals

**Goals:**
- Expose `GET /api/v1/pagos/{pedido_id}` returning all payment attempts for an order, ordered newest-first, with ownership enforcement
- Allow payment retry on a pedido with a rejected previous attempt by calling `POST /api/v1/pagos/crear` with a new idempotency key
- Generate unique `external_reference` per attempt to avoid unique constraint violations
- Preserve all prior payment records for audit trail
- Reuse existing schemas, models, and repository methods where possible

**Non-Goals:**
- No DDL or migration changes (model already supports 1:N)
- No changes to the webhook processing logic
- No changes to the pedido state machine (PENDIENTE on rejection already correct)
- No cancellation of pending payments on retry (old attempts remain visible)
- No frontend changes — API-only scope

## Decisions

### D1 — external_reference generation: append attempt number

**Decision:** Generate `external_reference` as `"{pedido_id}-{attempt}"` where `attempt = existing_pagos_count + 1`.

**Alternatives considered:**
- *Use `idempotency_key` as `external_reference`*: Technically unique but loses semantic value — `external_reference` is the merchant-facing field in MercadoPago's dashboard, so it should be human-readable. `idempotency_key` is a UUID, opaque in the MP backend.
- *Append a timestamp*: Unnecessary precision; attempt number is sufficient and more readable.

**Why:** The attempt counter is deterministic, human-readable in the MP dashboard (e.g., "42-1", "42-2"), monotonic, and completely avoids uniqueness clashes. It also makes it immediately obvious how many retries have occurred from the external_reference alone.

**Implementation:** Count existing `Pago` records for the pedido before creating, then set `external_reference = f"{pedido.id}-{count + 1}"`.

### D2 — GET endpoint: return list of PagoRead records

**Decision:** `GET /api/v1/pagos/{pedido_id}` returns `list[PagoRead]` ordered by `created_at DESC`.

**Alternatives considered:**
- *Return single latest payment only*: Insufficient for client-side retry UX — the client needs to see all attempts to display history.
- *Custom response schema with summary*: Over-engineered — `PagoRead` already has all fields needed (status, amount, timestamps). The client can derive "latest attempt" from position [0].

**Why:** Reuses existing `PagoRead` schema, avoids schema churn. The `get_by_pedido()` repository method already returns ordered results. Ownership enforcement aligns with other endpoints: client sees own orders, admin sees all.

**Implementation:**
- Router: `@router.get("/{pedido_id}", response_model=list[PagoRead])`
- Service: loads pedido, checks ownership, delegates to `uow.repos.pagos.get_by_pedido(pedido_id)`
- Auth: requires CLIENT or ADMIN role

### D3 — Retry validation: reject when approved payment exists or pedido not PENDIENTE

**Decision:** Add a pre-check in `crear_pago()` that rejects retries when:
1. pedido is not in PENDIENTE state (already exists)
2. The most recent payment for this pedido is already `approved`

**Rationale:**
- Condition 1 is already enforced by RN-PA06
- Condition 2 prevents double-payment: if a previous attempt succeeded (even if the order FSM hasn't advanced), no further attempts are allowed. This is a safety net against race conditions between webhook processing and retry creation.
- If the most recent payment is `rejected` or `cancelled`, retry is allowed.

**Implementation:** After loading pedido, query `get_by_pedido()` and check if any existing pago has `mp_status == "approved"`. If yes, raise `ConflictException("PAGO_YA_APROBADO")`.

### D4 — Idempotency: no changes needed

**Decision:** Keep the existing idempotency mechanism unchanged. Each call to `crear_pago` generates a fresh `uuid.uuid4()` as `idempotency_key`, which is already unique. The unique constraint on `idempotency_key` remains unchanged at the DB level.

**Why:** The idempotency key protects against MP API double-charges. Retries inherently produce new keys, so no collision risk. The existing mechanism is correct as-is.

### D5 — Reuse existing schemas without modification

**Decision:** `PagoRead` already has all fields needed for status query (status, amount, timestamps, external_reference). `CrearPagoRequest` and `PagoResponse` remain unchanged. No new schemas introduced.

**Why:** Schema minimization reduces review surface and avoids duplication. The only change is in `external_reference` value generation, not in the schema fields.

## Risks / Trade-offs

- **[Retry race condition]** If the webhook processes an approval concurrently with a retry request, both could succeed, creating two approved payments for one pedido. → Mitigation: the `mp_payment_id` unique constraint prevents duplicate MP payments. The `avanzar_estado` call in the webhook will fail on the second attempt (state already CONFIRMADO). At worst, one extra Pago record is created with `mp_status=approved` but the pedido never double-advances.
- **[Attempt counter gap]** If payments are deleted or failed pre-persist, the attempt counter may skip numbers. → Accepted: cosmetic only. `external_reference` is not a sequence — gaps are harmless.
- **[No cleanup for stale pending payments]** If MP returns `pending` and the user retries, the old pending record remains. → Accepted: this is by design (audit trail). The client can see the full history.
- **[GET endpoint leaks pedido existence]** Returning 404 for non-owned pedidos reveals existence information. → Mitigation: already standard in this API (same pattern as the creation endpoint). Return 404 for both "not found" and "not owned" to avoid existence oracle.
