## Context

El backend FSM valida las transiciones y los roles en `avanzar_estado()` del service. El frontend ya tiene `avanzarEstado()` en `entities/pedidos/api.ts` y los tipos `AvanzarEstadoRequest`. Lo único que falta es el hook de mutación y el componente UI que lo invoque.

La `PedidoDetailPage` ya muestra el cancel button para los roles que pueden cancelar (`canCancel` de `useCancelarPedido`). El mismo patrón aplica aquí: una función `canAdvance` / `getNextState` determina si mostrar el botón y cuál es el estado destino.

## Goals / Non-Goals

**Goals:**
- `useAvanzarEstado` hook con invalidación del pedido al completar
- Helper `getNextState(currentState, roles)` — retorna el próximo estado o null si el usuario no puede avanzar
- Botón "Avanzar a [estado]" en `PedidoDetailPage` visible solo para GESTOR/ADMIN cuando corresponde
- Ruta `/admin/pedidos` bajo `AdminRoute` que reutiliza `PedidoListPage`

**Non-Goals:**
- Nueva página de administración de pedidos (ya existe `PedidoListPage` que sirve a todos los roles)
- Filtros adicionales en el listado admin (ya implementados en 5.6)
- Dashboard de métricas de pedidos (7.1)

## Decisions

### D1: FSM map en el frontend — duplicar vs. confiar en el backend

**Decisión:** Mantener un mapa FSM mínimo en el frontend para determinar qué botón mostrar, con el entendimiento de que el backend valida definitivamente. El error del backend se muestra en un toast si la transición falla.

**Alternativa descartada:** No tener FSM frontend y mostrar siempre el botón — genera UX confusa (botón que falla en estados terminales).

**FSM map frontend:**
```
CONFIRMADO → EN_PREP (roles: PEDIDOS, ADMIN)
EN_PREP    → EN_CAMINO (roles: PEDIDOS, ADMIN)
EN_CAMINO  → ENTREGADO (roles: PEDIDOS, ADMIN)
```
PENDIENTE no tiene avance manual (solo vía pago). CANCELADO y ENTREGADO son terminales.

### D2: `getNextState` como helper puro en constants.ts

**Decisión:** Agregar `getNextState(currentState: string, roles: string[]): string | null` en `constants.ts` junto a `statusColors` y `statusLabels`. Retorna el código del siguiente estado o `null` si no hay transición válida para ese usuario.

**Razón:** Colocaliza la lógica FSM con los mapas de estado ya existentes. Es una función pura testeable.

### D3: Sin modal de confirmación para avanzar estado

**Decisión:** El avance de estado es una acción directa (botón → mutación). Solo cancelar pide confirmación (ya existe `CancelarPedidoModal`). Avanzar no requiere confirmación — es reversible solo en ciertos estados y el backend actúa como guardrail.

**Trade-off:** Si el usuario hace clic por error, no puede deshacer (excepto cancelar si aplica). Aceptado — los avances de estado son acciones deliberadas en un contexto de gestión.

### D4: Ruta `/admin/pedidos` reutiliza `PedidoListPage`

**Decisión:** `/admin/pedidos` renderiza `PedidoListPage` directamente. No se crea un componente wrapper.

**Razón:** `PedidoListPage` ya tiene comportamiento role-aware (título "Pedidos" para ADMIN/GESTOR, muestra todos los pedidos). El AdminRoute garantiza que solo ADMIN accede a esta ruta.

## Risks / Trade-offs

- **[Estado desactualizado]** Si otro usuario avanza el estado concurrentemente, el botón puede mostrar un estado incorrecto hasta el refetch → la mutación `useAvanzarEstado` invalida el query del pedido, forzando refetch.
- **[FSM duplicada]** El mapa frontend puede desincronizarse con el backend → aceptado para el scope; el backend es la fuente de verdad y retorna 400 si la transición no es válida.
