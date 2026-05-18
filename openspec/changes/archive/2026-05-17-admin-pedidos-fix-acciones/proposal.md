## Why

El admin de pedidos (`/admin/pedidos`) tiene 3 bugs en las acciones de cambio de estado: (1) el botón "Avanzar estado" no aparece para pedidos en PENDIENTE, (2) la FSM está duplicada e inconsistente entre la tabla y el detalle, y (3) desde la tabla solo se puede avanzar a un estado fijo mientras que el detalle permite elegir entre múltiples destinos.

## What Changes

- Centralizar `ADMIN_TRANSITIONS` en `frontend/src/entities/pedidos/constants.ts` con el mapa completo de transiciones (incluyendo PENDIENTE y múltiples destinos por estado).
- Reemplazar `FSM_TRANSITIONS` (lineal) por el mapa completo de transiciones que soporte múltiples destinos por estado.
- Actualizar `getNextState()` para que retorne `string[]` en lugar de `string | null`, reflejando todos los destinos válidos.
- Refactor `AdminPedidosPage.tsx` para que la acción "Avanzar estado" ofrezca un selector de estado destino (como ya hace `AdminPedidoDetailPage.tsx`) en lugar de un avance lineal fijo.
- Eliminar la `ADMIN_TRANSITIONS` duplicada en `AdminPedidoDetailPage.tsx` e importarla desde `constants.ts`.
- Corregir la lógica de cancelación en la tabla para que respete `canCancel()` (o equivalente) como ya hace el detalle.

## Capabilities

### New Capabilities
- `admin-order-fsm-actions`: Centraliza la FSM de transiciones admin con múltiples destinos por estado, unificando tabla y detalle.

### Modified Capabilities
- `admin-order-table`: La columna de acciones cambia de un avance lineal a un selector de estado destino con múltiples opciones.
- `admin-order-actions`: Se actualiza el menú de acciones rápidas para soportar selección de estado destino desde la tabla.
- `order-state-machine`: Se expone el mapa completo de transiciones admin desde `constants.ts` para consumo centralizado del frontend.

## Impact

- `frontend/src/entities/pedidos/constants.ts` — reemplazar `FSM_TRANSITIONS` por `ADMIN_TRANSITIONS`, actualizar `getNextState()`.
- `frontend/src/pages/admin/AdminPedidosPage.tsx` — refactor del dropdown de acciones para soportar múltiples destinos.
- `frontend/src/pages/admin/AdminPedidoDetailPage.tsx` — eliminar `ADMIN_TRANSITIONS` local, importar desde constants.
