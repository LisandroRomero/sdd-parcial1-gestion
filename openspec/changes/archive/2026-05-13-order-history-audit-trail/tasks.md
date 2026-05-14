## 1. Backend — Guard de autorización en GET /{id}/historial

- [x] 1.1 Agregar guard de autorización en `router.py:get_historial_pedido` replicando el patrón de `get_pedido` (router.py:128-131): CLIENT puro solo ve historial propio, ADMIN/GESTOR_PEDIDOS ve cualquiera
- [x] 1.2 Verificar que el endpoint responde 403 `PEDIDO_NO_AUTORIZADO` cuando CLIENT consulta historial ajeno, y 200 en casos autorizados

## 2. Frontend — Constantes compartidas statusColors / statusLabels

- [x] 2.1 Extraer `statusColors` y `statusLabels` de `PedidoDetailPage.tsx` a `entities/pedidos/constants.ts`
- [x] 2.2 Actualizar imports en `PedidoDetailPage.tsx` para usar las nuevas constantes compartidas

## 3. Frontend — Componente OrderTimeline

- [x] 3.1 Crear `entities/pedidos/ui/OrderTimeline/OrderTimeline.tsx` con la lógica del timeline vertical: círculo coloreado, línea conectora, nombre del estado, transición "desde {estado_desde}", timestamp con locale es-AR, motivo opcional
- [x] 3.2 Crear `entities/pedidos/ui/OrderTimeline/index.ts` con re-export
- [x] 3.3 Manejar array vacío: no renderizar nada (null / empty fragment)
- [x] 3.4 Reemplazar timeline inline en `PedidoDetailPage.tsx` por `<OrderTimeline historial={pedido.historial_estados} />`

## 4. Backend — Tests de integración

- [x] 4.1 Crear `backend/tests/test_pedidos_historial.py` con fixture de datos (pedido + historial con múltiples transiciones)
- [x] 4.2 Test: CLIENT ve su propio historial → 200 con datos correctos
- [x] 4.3 Test: CLIENT no ve historial ajeno → 403 Forbidden
- [x] 4.4 Test: ADMIN ve historial de cualquier pedido → 200
- [x] 4.5 Test: GESTOR_PEDIDOS ve historial de cualquier pedido → 200
- [x] 4.6 Test: pedido inexistente devuelve 404 NotFound
- [x] 4.7 Test: integridad de datos — orden cronológico ASC, primera entrada con `estado_desde = NULL`, `estado_hasta`, `motivo`, `usuario_id`
