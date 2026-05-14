## Why

El módulo de pedidos tiene el backend completo (listado, detalle, FSM, cancelación) y la vista de detalle individual implementada en frontend, pero **no existe una página de listado de pedidos**. Los usuarios no pueden ver sus pedidos históricos ni los gestores pueden administrarlos desde una vista de lista. Esto bloquea los cambios dependientes `5.6 frontend-order-history` y `7.4 admin-order-management`.

## What Changes

- **Nueva página de listado de pedidos** (`/pedidos` y `/mis-pedidos`) con tabla/cards responsive
- **Componentes de listado**: `OrderCard` (compacto), `OrderFilters` (filtros por estado y fechas), `OrderList` (con paginación)
- **Ruteo**: agregar rutas `/pedidos` (admin/gestor ve todos) y `/mis-pedidos` (cliente ve propios)
- **Separación de schemas**: `PedidoRead` (compacto para listados) vs `PedidoDetail` (completo con historial + datos de pago para detalle)
- **Paginación unificada**: migrar de `limit/offset` a `page/size` para alinear con la especificación del integrador
- **Sidebar/Nav**: agregar entrada "Mis Pedidos" en la navegación del cliente

## Capabilities

### New Capabilities
- `order-list-ui`: Página de listado de pedidos con filtros (estado, fechas), paginación `page/size`, cards responsive, y diferenciación por rol (CLIENT ve propios, ADMIN/PEDIDOS ve todos)

### Modified Capabilities
- `order-state-machine`: Actualizar schemas `PedidoRead` → separar en `PedidoRead` (compacto) y `PedidoDetail` (completo con historial + pago). Migrar paginación de `limit/offset` a `page/size` con `total`, `page`, `size`, `pages`.

## Impact

- **Frontend**: nuevas páginas, componentes, rutas, y navegación
- **Backend**: cambios en schemas de pedidos (`schemas.py`), ajuste menor en router (`limit/offset` → `page/size`), repository (contar total para paginación)
- **Dependencias**: desbloquea `5.6 frontend-order-history` y `7.4 admin-order-management`
- **Docs**: actualizar ejemplos de respuesta en `docs/Integrador.txt` si cambian los schemas
