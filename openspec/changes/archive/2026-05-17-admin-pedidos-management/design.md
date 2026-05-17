## Context

El backend de pedidos está completo: endpoints `PATCH /{id}/estado`, `DELETE /{id}`, `GET /{id}`, `GET /` con roles ADMIN, PEDIDOS y CLIENT ya implementados. El frontend tiene `PedidoListPage` (cards) y `PedidoDetailPage` con botón "Avanzar a X" para admin/gestores.

Sin embargo:
- `/admin/pedidos` usa el mismo componente `PedidoListPage` — sin tabla, sin vista admin dedicada
- No hay acciones rápidas desde el listado (hay que entrar al detalle)
- En el detalle el avance es secuencial (solo "siguiente" estado), sin selector de estado destino
- No hay invalidación cruzada: si ADMIN cambia un estado, el CLIENT no lo ve hasta que recarga manualmente

## Goals / Non-Goals

**Goals:**
- Crear `AdminPedidosPage.tsx` con vista tabular, filtros avanzados, acciones rápidas (avanzar estado, cancelar, ver detalle)
- Crear `AdminPedidoDetailPage.tsx` con selector de estado destino (no solo el "siguiente") y cancelación con motivo
- Actualizar `router.tsx` para las nuevas rutas admin
- Invalidación cruzada de TanStack Query para que cambios de admin se reflejen en el cliente
- Reutilizar al máximo componentes existentes (OrderCard, OrderTimeline, CancelarPedidoModal, etc.)

**Non-Goals:**
- No se modifica el backend (no es necesario)
- No se modifica `PedidoListPage` ni `PedidoDetailPage` para usuarios CLIENT
- No se implementa WebSockets ni polling en tiempo real (la invalidación vía queryClient es suficiente)
- No se implementa asignación de gestores a pedidos

## Decisions

### Decision 1: Tabla admin separada vs mejorar PedidoListPage existente
**Decisión**: Crear `AdminPedidosPage.tsx` separada.
**Rationale**: La UX de admin (tabla con columnas, ordenamiento, acciones inline) es radicalmente diferente a la vista de cliente (cards). Mezclarlas en un solo componente añadiría complejidad condicional excesiva. Las páginas admin existentes (AdminUsuariosPage, AdminProductosPage) ya siguen este patrón de tabla separada.

### Decision 2: Selector de estado destino en detalle admin
**Decisión**: En `AdminPedidoDetailPage`, mostrar un `<select>` con todos los estados destino válidos según la FSM, no solo el "siguiente".
**Rationale**: Un admin/gestor puede necesitar avanzar múltiples estados (ej: de CONFIRMADO a EN_CAMINO si hay confianza). El FSM valida del lado del backend, así que el frontend puede ofrecer todas las opciones válidas. Se reutiliza `useAvanzarEstado` hook.

### Decision 3: Invalidación cruzada para sync de cambios
**Decisión**: En el `onSuccess` del hook `useAvanzarEstado`, además de invalidar `['pedido', pedidoId]` y `['pedidos']`, invalidar también cualquier query que el usuario dueño del pedido pueda tener activa usando `queryClient.invalidateQueries({ queryKey: ['pedidos'] })` y `queryClient.invalidateQueries({ queryKey: ['pedido', pedidoId] })`. Esto es efectivo porque TanStack Query comparte el cache por queryKey, y si ambos usuarios (admin y client) están en la misma app, el client verá el cambio al refocusear la ventana.
**Rationale**: Es la solución más simple y efectiva sin agregar WebSockets. Si los usuarios están en diferentes navegadores, el refetch ocurrirá en la próxima interacción con la página (refocus, staleTime, o recarga manual).

### Decision 4: Filtros en AdminPedidosPage
**Decisión**: Agregar filtros adicionales a los existentes: búsqueda por nombre/apellido de usuario, select de estado, rango de fechas, y paginación.
**Rationale**: El endpoint `GET /pedidos` ya soporta `usuario_id` como filtro y `search` para buscar por ID o nombre de usuario. Se reutiliza `OrderFilters` extendiéndolo.

### Decision 5: Acciones rápidas inline en la tabla
**Decisión**: Cada fila de la tabla tendrá un menú de acciones (dropdown) con "Ver detalle", "Avanzar estado", "Cancelar pedido" según el estado actual.
**Rationale**: UX eficiente para admin sin necesidad de navegar al detalle para acciones comunes.

## Risks / Trade-offs

- [**Stale data**] La invalidación cruzada solo funciona si ambos usuarios están en el mismo navegador o si el CLIENT refocusa/recarga. → Mitigación: usar `refetchInterval: 30000` (30s) en las queries de pedidos para polling ligero.
- [**Complejidad de filtros**] Demasiados filtros pueden hacer la página lenta. → Mitigación: debounce en búsqueda (ya implementado), paginación server-side.
- [**Conflicto de concurrencia**] Dos admins cambiando el mismo pedido simultáneamente. → Mitigación: el backend maneja esto con validación de FSM; si la transición ya no es válida, devuelve error que el frontend muestra.
