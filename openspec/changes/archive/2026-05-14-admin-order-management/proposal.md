## Why

El backend FSM de pedidos está completamente implementado (5.2): `PATCH /api/v1/pedidos/{id}/estado` soporta todas las transiciones y valida roles. La función `avanzarEstado()` ya existe en el frontend (`entities/pedidos/api.ts`). Sin embargo, no hay ningún botón o UI en `PedidoDetailPage` que permita a GESTOR_PEDIDOS o ADMIN avanzar el estado de un pedido. Los gestores no pueden mover pedidos de CONFIRMADO→EN_PREPARACIÓN→EN_CAMINO→ENTREGADO desde el frontend.

## What Changes

- **Frontend — hook**: crear `useAvanzarEstado` (useMutation sobre la función `avanzarEstado` existente)
- **Frontend — helper FSM**: agregar `getNextState(currentState, roles)` en `entities/pedidos/constants.ts` — retorna el próximo estado válido dado el estado actual y los roles del usuario
- **Frontend — PedidoDetailPage**: agregar botón "Avanzar a [estado]" para usuarios GESTOR_PEDIDOS y ADMIN cuando el pedido tiene un siguiente estado válido en la FSM
- **Frontend — routing admin**: agregar ruta `/admin/pedidos` que reutiliza `PedidoListPage` bajo `AdminRoute` (punto de entrada admin para gestión de pedidos)

## Capabilities

### New Capabilities

- `admin-order-management-panel`: UI de gestión de pedidos para GESTOR_PEDIDOS y ADMIN — botón "Avanzar estado" en detalle de pedido + ruta `/admin/pedidos` dedicada.

### Modified Capabilities

_(ninguna — el cambio es puramente aditivo, sin cambios en specs existentes)_

## Impact

**Frontend:**
- `frontend/src/entities/pedidos/constants.ts` — agregar helper `getNextState`
- `frontend/src/features/pedidos/hooks/useAvanzarEstado.ts` — hook nuevo
- `frontend/src/pages/pedidos/PedidoDetailPage.tsx` — agregar sección de avance de estado
- `frontend/src/app/router.tsx` — agregar ruta `/admin/pedidos`
