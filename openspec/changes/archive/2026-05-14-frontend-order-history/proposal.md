## Why

La experiencia de "Mis Pedidos" está parcialmente construida (5.4, 5.5), pero US-049..US-051 tienen gaps concretos: el `OrderCard` no muestra la cantidad de ítems, el detalle no muestra la dirección de entrega snapshot, y los Gestores no pueden buscar pedidos por número o nombre de cliente. Este change cierra esos gaps para completar el flujo del cliente.

## What Changes

- **Backend — `PedidoRead`**: agregar `cantidad_items: int` (conteo de detalles, computed en la query)
- **Backend — `PedidoDetail`**: agregar `direccion` snapshot (calle, número, ciudad, provincia)
- **Backend — `GET /pedidos`**: agregar query param `buscar` para filtrar por ID de pedido o nombre/apellido de cliente (GESTOR/ADMIN)
- **Frontend — `OrderCard`**: mostrar `cantidad_items` junto a fecha y costo de envío
- **Frontend — `PedidoDetailPage`**: agregar sección "Dirección de entrega" con datos del snapshot
- **Frontend — `PedidoListPage`**: título dinámico "Mis Pedidos" (CLIENTE) / "Pedidos" (ADMIN, GESTOR_PEDIDOS)
- **Frontend — `OrderFilters`**: agregar input de búsqueda por número de pedido o cliente
- **Frontend — `types.ts`**: extender `PedidoRead` con `cantidad_items`, `PedidoDetail` con `DireccionSnapshot`, `ListarPedidosParams` con `buscar`

## Capabilities

### New Capabilities

- `order-detail-delivery-address`: Sección de dirección de entrega snapshot en `PedidoDetailPage`. Muestra calle, número, piso/depto, ciudad, provincia del snapshot al momento de creación del pedido.

### Modified Capabilities

- `order-list-ui`: Agregar `cantidad_items` al `OrderCard`, input de búsqueda en `OrderFilters`, y título role-aware en `PedidoListPage`.
- `pydantic-schemas`: Extender `PedidoRead` con `cantidad_items` (int) y `PedidoDetail` con `direccion` (DireccionSnapshot schema). Agregar param `buscar` a `GET /pedidos`.

## Impact

**Backend:**
- `backend/pedidos/schemas.py` — `PedidoRead` + `PedidoDetail` + nuevo `DireccionSnapshot`
- `backend/pedidos/repository.py` — query actualizada para incluir `cantidad_items` y `direccion` en joins
- `backend/pedidos/router.py` — param `buscar` en `GET /pedidos`

**Frontend:**
- `frontend/src/entities/pedidos/types.ts` — tipos actualizados
- `frontend/src/entities/pedidos/ui/OrderCard/OrderCard.tsx` — mostrar item count
- `frontend/src/pages/pedidos/PedidoListPage.tsx` — título dinámico + integrar `buscar`
- `frontend/src/pages/pedidos/PedidoDetailPage.tsx` — sección dirección de entrega
- `frontend/src/features/pedidos/components/OrderFilters.tsx` — input de búsqueda
