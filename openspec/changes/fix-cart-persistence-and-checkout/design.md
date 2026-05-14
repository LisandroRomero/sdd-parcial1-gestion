## Context

The cart store uses Zustand persist middleware with version 2 but lacks a custom merge function, causing derived state to keep initial values after hydration. The checkout page sends incorrect field names and omits required fields, resulting in 422 errors from the backend.

## Goals / Non-Goals

**Goals:**
- Cart derived state (`totalItems`, `totalPrice`, `isCartEmpty`) recalculates correctly after persist hydration
- Checkout payload matches backend expectations (`direccion_id`, `forma_pago_codigo`)
- `getItemsForCheckout` uses `personalizacion` field name
- Version bumps are handled via `migrate` function

**Non-Goals:**
- Creating a full payment method selector UI (forma_pago_codigo uses default "EFECTIVO")
- Refactoring the entire cart store architecture

## Decisions

### D1: Selectors over derived state
Move `totalItems`, `totalPrice`, `isCartEmpty` to computed selectors (getters via `useCartStore` selectors) instead of persisting them as state fields. This ensures values are always computed from the source of truth (`items`).

### D2: Merge strategy
Add custom `merge` function to Zustand persist middleware that recalculates all derived state after hydration from the persisted `items` array. Combined with `partialize` to only persist `items`.

### D3: forma_pago_codigo default
Hardcode `"EFECTIVO"` as the default forma_pago_codigo since there is no payment method selector yet. This avoids blocking checkout while keeping the door open for a future payment flow component.

## Risks / Trade-offs

- Hardcoding "EFECTIVO" means all orders default to cash payment until a selector is built
- Removing `precio_unitario` from `getItemsForCheckout` return is a breaking change if any other code depends on it (verified: it's only used by checkout)
