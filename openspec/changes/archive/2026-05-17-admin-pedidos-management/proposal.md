## Why

Actualmente los administradores no tienen una interfaz dedicada para gestionar pedidos. Al navegar a `/admin/pedidos` ven la misma lista de tarjetas (OrderCard) que un usuario cliente, sin acciones rápidas ni vista tabular. Aunque el backend ya soporta el cambio de estado con roles ADMIN/PEDIDOS, el frontend carece de una experiencia admin adecuada. Además, cuando un admin cambia un estado, el usuario dueño del pedido no ve el cambio reflejado automáticamente porque los datos cacheados no se invalidan del otro lado.

## What Changes

- Crear `AdminPedidosPage.tsx` — página dedicada con tabla de pedidos, filtros avanzados (búsqueda, estado, fechas, usuario) y acciones rápidas (avanzar estado, cancelar) directamente desde la tabla
- Crear `AdminPedidoDetailPage.tsx` — detalle admin con selector de estado destino (no solo el "siguiente" automático) y capacidad de cancelar con motivo
- Actualizar `router.tsx` para que `/admin/pedidos` use `AdminPedidosPage` y `/admin/pedidos/:id` use `AdminPedidoDetailPage`
- Agregar invalidación cruzada de TanStack Query para que cuando un admin cambie un estado, el usuario dueño del pedido vea los cambios reflejados al recargar su lista/detalle
- Agregar hook `useListarPedidosAdmin` con filtros adicionales (búsqueda por usuario, todos los pedidos sin filtrar por user_id)

## Capabilities

### New Capabilities
- `admin-order-table`: Vista tabular de pedidos para admin con columnas (ID, usuario, estado, total, fecha) y ordenamiento
- `admin-order-actions`: Acciones rápidas de cambio de estado y cancelación desde tabla y detalle admin
- `order-refresh-sync`: Invalidación automática de queries de pedidos del usuario cuando admin modifica estados

### Modified Capabilities
- `admin-order-management-panel`: Se actualiza la spec existente para reflejar que ahora hay una página admin dedicada (no solo la ruta)

## Impact

- **Frontend**: Nuevos archivos en `frontend/src/pages/admin/` (AdminPedidosPage, AdminPedidoDetailPage), modificación de `router.tsx`
- **Backend**: Sin cambios — los endpoints existentes ya soportan todos los roles necesarios
- **Queries**: Se agrega lógica de invalidación de TanStack Query para sync cross-user
