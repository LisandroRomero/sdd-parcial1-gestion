## 1. Cart Store Hydration Fix

- [x] 1.1 Add custom `merge` function to persist middleware that recalculates derived state after hydration
- [x] 1.2 Convert totalItems, totalPrice, isCartEmpty to computed selectors (not stored state)
- [x] 1.3 Add `migrate` function for version 2 &rarr; handle potential future version bumps

## 2. Checkout Payload Fix

- [x] 2.1 Fix direccion_entrega_id &rarr; direccion_id in CheckoutPage.tsx
- [x] 2.2 Add forma_pago_codigo to checkout mutation payload (default: "EFECTIVO")
- [x] 2.3 Fix ingredientes_excluidos &rarr; personalizacion in cart.store.ts getItemsForCheckout
- [x] 2.4 Remove precio_unitario from getItemsForCheckout return (not in type)

## 3. Verify

- [x] 3.1 Verify cart persists across navigation after fix
- [x] 3.2 Verify checkout API call succeeds with corrected payload
