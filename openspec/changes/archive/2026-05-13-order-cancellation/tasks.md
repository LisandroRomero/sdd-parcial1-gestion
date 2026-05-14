## 1. Feature Hook — `useCancelarPedido`

- [x] 1.1 Create `frontend/src/features/pedidos/hooks/useCancelarPedido.ts` with TanStack Query `useMutation` wrapping `cancelarPedido` from entities
- [x] 1.2 Configure `onSuccess` to invalidate `['pedidos']` query key and `['pedido', pedidoId]` for automatic refetch
- [x] 1.3 Add client-side role validation guard inside the hook (CLIENTE/ADMIN/GESTOR_PEDIDOS with their allowed estados)
- [x] 1.4 Map backend error codes (`PEDIDO_ESTADO_TERMINAL`, `PEDIDO_NO_ENCONTRADO`, etc.) to user-facing error messages

## 2. Component — `CancelarPedidoModal`

- [x] 2.1 Create `frontend/src/features/pedidos/components/CancelarPedidoModal.tsx` with modal overlay, close-on-escape, and close-on-backdrop-click
- [x] 2.2 Add predefined motivo radio list (e.g. "Ya no lo quiero", "Cambié de opinión", "Tiempo de espera muy largo", "Problema con el pago", "Otro")
- [x] 2.3 Add textarea for custom motivo (max 255 chars with character counter) when "Otro" is selected
- [x] 2.4 Wire confirm button to `useCancelarPedido` mutation, show loading spinner while submitting
- [x] 2.5 Show toast (success/error) on mutation settle; close modal on success
- [x] 2.6 Disable confirm button when no motivo selected or mutation is pending

## 3. Integration — Cancel Button on Order Detail

- [x] 3.1 Add contextual cancel button to order detail page, visible only when current role + estado matches allowed transitions
- [x] 3.2 Wire button click to open `CancelarPedidoModal` with the selected `pedidoId`
- [x] 3.3 Show loading/disabled state on the button while mutation is in-flight
- [x] 3.4 Handle edge case: pedido already cancelled on backend (stale UI) — refetch and show error toast

## 4. Checkout Confirmation — Link to Order Detail

- [x] 4.1 Add "Ver detalle del pedido" link on the checkout confirmation page pointing to the order detail route with the created `pedidoId`
- [x] 4.2 Ensure the link is only shown when the API response includes a valid `pedidoId`

## 5. Polish — Badge, Edge Cases, Error States

- [x] 5.1 Add red-styled CANCELADO badge/status chip to order cards and order detail (matching `estado === 'CANCELADO'`)
- [x] 5.2 Export `CancelarPedidoModal` and `useCancelarPedido` from `frontend/src/features/pedidos/index.ts`
- [x] 5.3 Verify all components handle loading, error, empty, and success states per project conventions
