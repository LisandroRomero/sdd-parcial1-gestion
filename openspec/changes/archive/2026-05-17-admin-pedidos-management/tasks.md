## 1. Hook admin para listar pedidos

- [x] 1.1 Crear hook `useListarPedidosAdmin` en `frontend/src/features/pedidos/hooks/` que use el endpoint `GET /pedidos` con filtros adicionales (búsqueda por nombre de usuario, sin filtrar por usuario propio) y soporte ordenamiento por columnas
- [x] 1.2 Agregar tipos para los parámetros de ordenamiento en `entities/pedidos/types.ts`

## 2. AdminPedidosPage — tabla de pedidos

- [x] 2.1 Crear `frontend/src/pages/admin/AdminPedidosPage.tsx` con tabla usando componentes base de Tailwind, columnas: ID, Usuario, Estado (badge), Ítems, Total, Fecha, Acciones
- [x] 2.2 Integrar filtros: búsqueda (con debounce), selector de estado, rango de fechas, paginación — reutilizando `OrderFilters` y `OrderPagination` donde sea posible
- [x] 2.3 Agregar menú de acciones (dropdown de tres puntos) en cada fila con opciones contextuales según el estado: "Ver detalle", "Avanzar estado", "Cancelar pedido"
- [x] 2.4 Implementar acción rápida "Avanzar estado" desde la tabla con confirmación (select de estado destino + botón confirmar)
- [x] 2.5 Implementar acción rápida "Cancelar pedido" desde la tabla reutilizando `CancelarPedidoModal`
- [x] 2.6 Manejar estados visuales: loading (skeleton de tabla), error (con retry), empty (con mensaje), offline

## 3. AdminPedidoDetailPage — detalle admin

- [x] 3.1 Crear `frontend/src/pages/admin/AdminPedidoDetailPage.tsx` reutilizando componentes existentes (OrderTimeline, info del pedido, pago, dirección, productos)
- [x] 3.2 Agregar selector de estado destino (select con opciones válidas según FSM) + botón "Avanzar" — conectado a `useAvanzarEstado`
- [x] 3.3 Agregar botón "Cancelar pedido" con modal de motivo — conectado a `useCancelarPedido`
- [x] 3.4 Manejar estados visuales: loading, error (404 incluido), offline

## 4. Router y navegación

- [x] 4.1 Actualizar `frontend/src/app/router.tsx` para que `/admin/pedidos` use `AdminPedidosPage` y `/admin/pedidos/:id` use `AdminPedidoDetailPage`

## 5. Invalidación cruzada y sync

- [x] 5.1 Modificar `useAvanzarEstado` para que en `onSuccess` invalide `['pedido', pedidoId]` y `['pedidos']` globalmente en el queryClient (no solo la key específica del admin)
- [x] 5.2 Modificar `useCancelarPedido` para que en `onSuccess` invalide `['pedidos']` y `['pedido', pedidoId]`
- [x] 5.3 Agregar `refetchInterval: 30000` a las queries `['pedidos', params]` en `useListarPedidos` para polling silencioso cada 30s
- [x] 5.4 Agregar `refetchInterval: 30000` a la query `['pedido', id]` en `PedidoDetailPage` para polling silencioso

## 6. Verificación

- [ ] 6.1 Verificar que admin puede ver tabla de pedidos con datos correctos
- [ ] 6.2 Verificar que admin puede cambiar estado desde tabla y detalle
- [ ] 6.3 Verificar que admin puede cancelar pedidos con motivo
- [ ] 6.4 Verificar que el usuario CLIENT ve los cambios de estado reflejados después del refetch
