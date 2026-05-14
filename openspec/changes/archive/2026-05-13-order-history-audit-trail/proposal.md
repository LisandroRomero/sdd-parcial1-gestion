## Why

El endpoint `GET /api/v1/pedidos/{id}/historial` ya existe y el modelo `HistorialEstadoPedido` ya se escribe correctamente en cada transición de estado (creación, avance, cancelación). Sin embargo, el endpoint carece de autorización: cualquier usuario autenticado puede ver el historial de cualquier pedido, incluso si no es su dueño. Esto viola RN-AC03 (propietario o administrador). Además, no hay validación explícita de que `motivo` sea requerido en transiciones de cancelación, ni existe componente frontend que visualice la línea de tiempo de estados. Sin este cambio, la auditoría de cambios de estado (US-044) no es accesible ni segura.

## What Changes

- Agregar autorización al endpoint `GET /{id}/historial`: CLIENT solo ve historial de sus propios pedidos; ADMIN y GESTOR_PEDIDOS ven cualquier historial
- Validar que `motivo` sea obligatorio en toda cancelación (a nivel service, consistente con RN-DA05)
- Crear componente frontend `OrderTimeline` en entities/pedidos que renderice la secuencia cronológica de estados con formato visual (timeline vertical)
- Integrar el timeline en la página de detalle de pedido
- Agregar tests del endpoint historial (autorización, filtrado, 404)
- Opcional: extraer `HistorialEstadoPedidoRepository` con métodos dedicados (`create`, `list_by_pedido`) en lugar de `session.add()` directo en service

## Capabilities

### New Capabilities
- `order-history-audit-trail`: Consulta del historial de cambios de estado de un pedido — endpoint autorizado con acceso según rol, componente visual de timeline con estados, fechas, usuario responsable y motivo, y soporte append-only con integridad referencial

### Modified Capabilities
- `order-fsm-and-state-transition`: El service de pedidos debe validar que `motivo` sea obligatorio en transiciones de cancelación, y el endpoint historial existente debe incorporar control de acceso por propietario/rol

## Impact

- **Backend**: `pedidos/router.py` — agregar guard de autorización (CLIENT vs ADMIN/PEDIDOS) en `get_historial_pedido`. `pedidos/service.py` — validar motivo requerido en cancelación. Opcional: `pedidos/repository.py` extraer repositorio dedicado de historial
- **Frontend**: nuevo componente `entities/pedidos/ui/OrderTimeline/` con timeline visual. Integración en página de detalle de pedido existente
- **Tests**: `backend/tests/test_pedidos_historial.py` — cobertura de autorización, datos, y 404
- **Docs**: actualizar `docs/Integrador.txt` con especificación del endpoint y reglas de acceso
- **Depende de**: backend de FSM de pedidos (change 5.1 — ya completado), backend de cancelación (change 5.2 — ya completado), schemas y modelo de historial (ya existentes)
