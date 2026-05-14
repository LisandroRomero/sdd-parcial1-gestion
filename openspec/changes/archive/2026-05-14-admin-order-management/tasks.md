## 1. Frontend — Helper FSM en constants

- [x] 1.1 En `frontend/src/entities/pedidos/constants.ts`, agregar la función `getNextState(currentState: string, roles: string[]): string | null`:
  - FSM map: `CONFIRMADO → "EN_PREP"`, `EN_PREP → "EN_CAMINO"`, `EN_CAMINO → "ENTREGADO"`
  - Solo retorna el siguiente estado si el usuario tiene rol `"PEDIDOS"` o `"ADMIN"`
  - Retorna `null` para PENDIENTE, ENTREGADO, CANCELADO o si el usuario no tiene los roles necesarios

## 2. Frontend — Hook useAvanzarEstado

- [x] 2.1 Crear `frontend/src/features/pedidos/hooks/useAvanzarEstado.ts`:
  - `useMutation` sobre `avanzarEstado` de `@/entities/pedidos`
  - `onSuccess`: llamar `queryClient.invalidateQueries({ queryKey: ['pedido', pedidoId] })` para refrescar el detalle
  - Exportar el hook y el tipo de la mutación

## 3. Frontend — Botón "Avanzar estado" en PedidoDetailPage

- [x] 3.1 En `frontend/src/pages/pedidos/PedidoDetailPage.tsx`:
  - Importar `getNextState` de `@/entities/pedidos/constants`
  - Importar `useAvanzarEstado` del nuevo hook
  - Calcular `nextState = getNextState(pedido.estado_actual, roles)` donde `roles` viene de `useAuthStore`
  - Si `nextState !== null`: mostrar botón `"Avanzar a {statusLabels[nextState]}"` junto al cancel button
  - Al hacer clic: llamar `avanzarMutation.mutate({ pedidoId: numericId, data: { nuevo_estado: nextState } })`
  - Si `avanzarMutation.isError`: mostrar el mensaje de error (similar al manejo existente de cancelación)
  - Deshabilitar el botón mientras `avanzarMutation.isPending`

## 4. Frontend — Ruta /admin/pedidos

- [x] 4.1 En `frontend/src/app/router.tsx`, dentro del grupo `AdminRoute` / `Layout`:
  - Agregar `{ path: 'pedidos', element: <PedidoListPage /> }` (reutilizar el componente existente sin lazy, ya está importado; si no está importado, importarlo)
