## Context

The backend already implements order cancellation fully: a `DELETE /api/v1/pedidos/{id}?motivo=...`
endpoint with FSM validation, role-based access (Admin, Gestor de Pedidos), stock restoration, and
audit trail entries. The `PedidoRead` response includes `historial_estados` with all state
transitions. Cancellation sets state to `CANCELADO`, which is a terminal state — no further
transitions are allowed.

On the frontend, the entities layer (`entities/pedidos/`) already defines TypeScript types
(`PedidoRead`, `HistorialEstadoRead`) and an API function `cancelarPedido(pedidoId, motivo)`.
No UI exists yet to trigger cancellation from the order detail page.

## Goals / Non-Goals

**Goals:**

- Expose a visual **Cancelar Pedido** button on the order detail page, visible only when the
  current user has the required role (Admin, Gestor de Pedidos) and the order is in a cancellable
  state (PENDIENTE, CONFIRMADO, EN_PREPARACION).
- Show a **modal** on click that collects a required `motivo` string before confirming cancellation.
- Add a `useCancelarPedido` TanStack Query mutation hook in a new `features/pedidos/` layer.
- Display a `CANCELADO` badge on the order header and a timeline entry in the order state
  history when the order is cancelled.
- Show toast notifications for success (order cancelled, stock restored) and error (reason).
- Invalidate related queries after successful cancellation so the UI reflects the new state.

**Non-Goals:**

- Editing backend cancellation logic, roles, or the FSM.
- Implementing payment refund logic (MercadoPago reverse/refund).
- Re-opening or re-activating a cancelled order.
- Deleting orders from the database.

## Decisions

1. **Modal pattern for motivo collection over inline confirmation**  
   A modal with a text area forces the user to provide the required cancellation reason, which is
   mandatory in the backend. An inline confirmation (e.g. SweetAlert prompt) would be more compact
   but harder to validate and harder to extend if additional fields are needed later.

2. **`features/pedidos/` over adding to `entities/pedidos/`**  
   The `entities/pedidos/api.ts` exposes the raw `cancelarPedido()` call — FSD rules say entities
   hold only types and API wrappers. The mutation hook (`useCancelarPedido`) and the modal
   component (`CancelarPedidoModal`) belong in `features/pedidos/` because they encapsulate
   UI + side-effect logic (toast, query invalidation).

3. **TanStack Query `useMutation` over Zustand for server state**  
   Cancellation is a server action with side effects (stock restoration). Zustand is reserved for
   client-only state (cart, UI flags). `useMutation` handles loading/error states, automatic
   invalidation, and optimistic updates natively. Using Zustand here would duplicate server state
   and break the project convention.

4. **Query invalidation over manual refetch**  
   After a successful cancel, invalidating `['pedido', pedidoId]` and `['pedidos']` via
   `queryClient.invalidateQueries` ensures all consumers re-fetch. A manual refetch would require
   passing refetch callbacks through the component tree and risks stale data.

5. **Role + state visibility via auth store read**  
   The cancel button visibility is computed from `authStore.user.roles` and
   `pedido.estado`. This is a pure render-time check — no new permission API call needed since
   the backend already enforces authorization and returns 403 if violated.

6. **Toast for feedback over inline error message**  
   Cancellation is a destructive action. A toast notification (success or error) is more visible
   than an inline message and follows the existing UI pattern for server actions in the project.

## Risks / Trade-offs

- **Race condition**: A user could click "Cancelar" moments after another operator advances the
  order. The backend FSM rejects the transition and the mutation returns a 409/400. The toast
  must clearly display the backend error message so the operator understands the order already
  moved to a non-cancellable state.

- **Stale query cache**: Other open tabs or components watching the same order (e.g. a real-time
  dashboard) will keep the old state until `invalidateQueries` completes. This is acceptable
  because TanStack Query's stale-while-revalidate strategy ensures eventual consistency.

- **Modal UX overhead**: For a quick cancellation, a modal is heavier than an inline prompt.
  Trade-off is deliberate: the `motivo` is mandatory (backend rejects without it), and a modal
  makes the reason field prominent, encouraging proper audit trail entries.
