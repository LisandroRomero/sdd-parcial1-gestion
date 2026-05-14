## Why

El backend de cancelación de pedidos está completamente implementado (change 5.2): FSM con 6 estados, endpoint `DELETE /api/v1/pedidos/{id}?motivo=...`, restauración de stock atómico y audit trail completo. Sin embargo, el frontend carece de cualquier interfaz para que usuarios y administradores ejecuten cancelaciones. Sin esta UI, la funcionalidad de cancelación es inaccesible para los usuarios del sistema.

## What Changes

- Crear feature `pedidos/` en capa features de FSD con hooks y componentes de cancelación
- Modal de cancelación con selector de motivo (predefinidos + texto libre) y botones confirmar/cancelar
- Integrar botón de cancelación en vistas de detalle y listado de pedidos (visible según estado y rol)
- Mutación TanStack Query para `cancelarPedido()` con invalidación de queries y optimistic UI
- Badge visual de estado `CANCELADO` con estilo diferenciado (rojo/neutral)
- Indicación visual en timeline/historial de estados para cancelaciones con motivo

## Capabilities

### New Capabilities
- `order-cancellation-ui`: Interfaz completa de cancelación — modal con entrada de motivo, hook `useCancelarPedido` con mutación TanStack Query, botón contextual de cancelación en vistas de pedido, badge de estado CANCELADO con estilo visual, y registro de la cancelación en el timeline del pedido

### Modified Capabilities
- `order-fsm-and-state-transition`: La UI de detalle de pedido debe exponer el botón de cancelación según reglas de estado y rol (CLIENTE solo en PENDIENTE, ADMIN en PENDIENTE/CONFIRMADO/EN_PREP, GESTOR_PEDIDOS en PENDIENTE/CONFIRMADO)
- `frontend-checkout-page`: La página de confirmación de pedido debe mostrar un enlace al detalle del pedido, donde el usuario podrá cancelarlo si es necesario

## Impact

- **Frontend only**: nueva feature `pedidos/` en `frontend/src/features/pedidos/` con hooks (`useCancelarPedido`, `usePedido`, `useListarPedidos`) y componentes modales (`CancelarPedidoModal`)
- **Entities**: `frontend/src/entities/pedidos/` ya existe — no requiere cambios mayores
- **Pages**: integrar botón de cancelación en páginas de detalle de pedido existentes o futuras
- **Depende de**: backend de cancelación (change 5.2 — ya completado)
