## Why

Five bugs in cart persistence and checkout payload cause data loss, incorrect derived state, and API 422 errors.

## What Changes

- Add custom `merge` function to Zustand persist middleware to recalculate derived state after hydration
- Convert `totalItems`, `totalPrice`, `isCartEmpty` to computed selectors instead of persisted state
- Add `migrate` function for persist version 2
- Fix `direccion_entrega_id` &rarr; `direccion_id` in CheckoutPage
- Add `forma_pago_codigo` to checkout mutation payload
- Fix `ingredientes_excluidos` &rarr; `personalizacion` in `getItemsForCheckout`
- Remove `precio_unitario` from `getItemsForCheckout` return

## Capabilities

### New Capabilities
- `cart-persistence-fix`: Fix Zustand persist hydration so derived state recalculates correctly
- `checkout-payload-fix`: Fix field names and add missing required fields in checkout mutation

### Modified Capabilities
- `client-state`: Fix cart store hydration logic and derived state computation
- `shopping-cart`: Add merge/migrate strategy for persist middleware

## Impact

- `frontend/src/shared/lib/stores/cart.store.ts` &mdash; Fix persist merge, add migrate or recompute on hydration, fix getItemsForCheckout field names
- `frontend/src/pages/checkout/CheckoutPage.tsx` &mdash; Fix direccion_entrega_id &rarr; direccion_id, add forma_pago_codigo
