## 1. Backend — Schemas y paginación

- [x] 1.1 Separar `PedidoRead` (compacto) y crear `PedidoDetail` (completo con historial + pago) en `backend/pedidos/schemas.py`
- [x] 1.2 Crear schema `PagoResumen` para incluir en `PedidoDetail` (id, estado_pago, metodo_pago, monto)
- [x] 1.3 Migrar `GET /api/v1/pedidos/` de `limit/offset` a `page/size` con respuesta `{ items, total, page, size, pages }`
- [x] 1.4 Agregar filtros `fecha_desde` y `fecha_hasta` en `GET /api/v1/pedidos/` (repository + router)
- [x] 1.5 Actualizar `PedidoListRead` para usar el formato `page/size`
- [x] 1.6 Mantener backward compatibility: aceptar `limit/offset` como deprecados y convertir internamente
- [x] 1.7 Agregar índice compuesto `(usuario_id, created_at)` en modelo `Pedido` para optimizar queries de listado

## 2. Frontend — Componente OrderCard

- [x] 2.1 Crear componente `OrderCard` en `entities/pedidos/ui/OrderCard/OrderCard.tsx` con: ID formateado, badge de estado con color, monto total, fecha, costo de envío
- [x] 2.2 Hacer `OrderCard` clickeable navegando a `/pedidos/{id}`
- [x] 2.3 Cubrir estados: loading (skeleton), error, empty en `OrderCard`

## 3. Frontend — Página de listado de pedidos

- [x] 3.1 Crear hook `useListarPedidos` en `features/pedidos/hooks/` con TanStack Query y paginación `page/size`
- [x] 3.2 Actualizar `entities/pedidos/api.ts`: adaptar `listarPedidos` para usar `page/size` y filtros
- [x] 3.3 Crear componente `OrderFilters` en `features/pedidos/components/OrderFilters.tsx` con: select de estado, datepicker de rango, botón limpiar
- [x] 3.4 Crear componente `OrderPagination` en `features/pedidos/components/OrderPagination.tsx` con navegación entre páginas
- [x] 3.5 Crear `PedidoListPage` en `pages/pedidos/PedidoListPage.tsx` integrando `OrderCard`, `OrderFilters`, `OrderPagination`
- [x] 3.6 Agregar estado empty: mensaje "No tienes pedidos aún" con botón a catálogo
- [x] 3.7 Agregar estado error con botón "Reintentar"

## 4. Frontend — Ruteo y navegación

- [x] 4.1 Agregar ruta protegida `/pedidos` → `PedidoListPage` en `app/router.tsx`
- [x] 4.2 Agregar entrada "Mis Pedidos" (CLIENTE) / "Pedidos" (ADMIN, GESTOR_PEDIDOS) en el menú de navegación lateral/superior
- [x] 4.3 Verificar que `/pedidos/:id` (detalle existente) sigue funcionando correctamente

## 5. Frontend — Adaptar PedidoDetailPage a PedidoDetail schema

- [x] 5.1 Actualizar `PedidoDetailPage` para consumir `PedidoDetail` (con campo `pago`) en lugar de `PedidoRead`
- [x] 5.2 Mostrar información de pago en el detalle del pedido (estado, método, monto)
- [x] 5.3 Actualizar tipos en `entities/pedidos/types.ts` con `PedidoRead` compacto y `PedidoDetail`

## 6. Verificación y sync

- [x] 6.1 Verificar que todos los tests existentes del backend de pedidos siguen pasando
- [x] 6.2 Verificar que el frontend compila sin errores de tipo
- [x] 6.3 Actualizar `docs/Integrador.txt` con los ejemplos de respuesta actualizados (page/size, PedidoDetail)
- [ ] 6.4 Sync specs a `openspec/specs/` — archivar el change
