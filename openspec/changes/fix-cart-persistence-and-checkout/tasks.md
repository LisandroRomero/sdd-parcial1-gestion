## 1. Cart Store Hydration Fix

- [ ] 1.1 Add custom `merge` function to persist middleware that recalculates derived state after hydration
- [ ] 1.2 Convert totalItems, totalPrice, isCartEmpty to computed selectors (not stored state)
- [ ] 1.3 Add `migrate` function for version 2 &rarr; handle potential future version bumps

## 2. Checkout Payload Fix

- [ ] 2.1 Fix direccion_entrega_id &rarr; direccion_id in CheckoutPage.tsx
- [ ] 2.2 Add forma_pago_codigo to checkout mutation payload (default: "EFECTIVO")
- [ ] 2.3 Fix ingredientes_excluidos &rarr; personalizacion in cart.store.ts getItemsForCheckout
- [ ] 2.4 Remove precio_unitario from getItemsForCheckout return (not in type)

## 3. Verify

- [ ] 3.1 Verify cart persists across navigation after fix
- [ ] 3.2 Verify checkout API call succeeds with corrected payload
