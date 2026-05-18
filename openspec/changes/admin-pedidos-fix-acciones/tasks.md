## 1. FSM Centralization

- [x] 1.1 Replace `FSM_TRANSITIONS` in `frontend/src/entities/pedidos/constants.ts` with `ADMIN_TRANSITIONS` (Record<string, string[]>) with full map including PENDIENTE
- [x] 1.2 Rename `getNextState()` to `getAdminNextStates()` returning `string[]` instead of `string | null`
- [x] 1.3 Remove duplicate `ADMIN_TRANSITIONS` from `frontend/src/pages/admin/AdminPedidoDetailPage.tsx` and import from `constants.ts`
- [x] 1.4 Update imports in `AdminPedidoDetailPage.tsx`: replace local constant usage with `getAdminNextStates`

## 2. Table Actions Refactor

- [x] 2.1 Update `AdminPedidosPage.tsx`: import `getAdminNextStates` instead of `getNextState`
- [x] 2.2 Refactor the "Avanzar estado" dropdown in the table to show a selector with multiple destination states (inline row with select + confirm/cancel buttons)
- [x] 2.3 Update `advanceMutation` call to use the selected destination state instead of a fixed next state

## 3. Verification

- [x] 3.1 Verify "Avanzar estado" appears for PENDIENTE orders in the admin table — verificación visual/código: `getAdminNextStates('PENDIENTE', ['ADMIN'])` retorna `['CONFIRMADO', 'CANCELADO']`, por lo que `nextStates.length > 0` es true y el botón aparece
- [x] 3.2 Verify multiple destination options appear in the table inline selector (e.g., PENDIENTE → CONFIRMADO or CANCELADO) — verificación visual/código: el select renderiza un `<option>` por cada elemento de `nextStates`; para PENDIENTE son CONFIRMADO y CANCELADO
- [x] 3.3 Verify detail page still works and shows the same transitions via the centralized import — verificación visual/código: `AdminPedidoDetailPage.tsx` importa `getAdminNextStates` desde `constants.ts`, eliminando el mapa duplicado local
- [x] 3.4 Verify terminal states (ENTREGADO, CANCELADO) don't show "Avanzar estado" — verificación visual/código: `ADMIN_TRANSITIONS['ENTREGADO']` y `ADMIN_TRANSITIONS['CANCELADO']` son `[]`, por lo que `nextStates.length > 0` es false
