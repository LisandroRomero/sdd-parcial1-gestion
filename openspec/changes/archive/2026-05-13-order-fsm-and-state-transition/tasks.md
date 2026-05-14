## 1. Migración y Seed

- [x] 1.1 Crear migración Alembic que agregue `usuario_id` (FK → usuarios.usuario.id, nullable) y `motivo` (VARCHAR(255), nullable) a `HistorialEstadoPedido`
- [x] 1.2 Actualizar `backend/scripts/seed.py`: renombrar `PREPARACION → EN_PREP` y `ENVIADO → EN_CAMINO` en la tabla `EstadoPedido`, ajustar `es_terminal` si es necesario

## 2. Modelos y Schemas

- [x] 2.1 Actualizar `backend/pedidos/model.py`: agregar campos `usuario_id: Optional[int]` y `motivo: Optional[str]` a `HistorialEstadoPedido`
- [x] 2.2 Agregar `forma_pago_codigo: str` como campo obligatorio en `PedidoCreate` schema
- [x] 2.3 Agregar `historial_estados: list[HistorialEstadoRead]` en `PedidoRead` schema
- [x] 2.4 Crear schema `AvanzarEstadoRequest` con `nuevo_estado: str` y `motivo: Optional[str]` validando motivo no vacío
- [x] 2.5 Crear schema `HistorialEstadoRead` para exponer historial en respuestas
- [x] 2.6 Crear schema `PedidoListRead` con paginación para listar pedidos
- [x] 2.7 Eliminar campo `estado_actual` de `PedidoUpdate` (las transiciones tienen su propio schema)

## 3. Repository

- [x] 3.1 Agregar método `get_by_id_with_user_check(pedido_id, usuario_id)` a `PedidoRepository` que verifique pertenencia
- [x] 3.2 Agregar método `list_pedidos(usuario_id=None, estado=None, limit=20, offset=0)` con filtros
- [x] 3.3 Agregar método `get_historial(pedido_id)` que devuelve historial ordenado por `created_at`
- [x] 3.4 Agregar método `get_productos_by_pedido(pedido_id)` para rollback de stock
- [x] 3.5 Agregar método `restaurar_stock_productos(productos_stock: list[tuple[int, int]])` para rollback

## 4. Service — FSM Engine

- [x] 4.1 Definir mapa `TRANSICIONES_VALIDAS` como dict inmutable con `{origen: {destino: set[roles]}}`
- [x] 4.2 Implementar método `_validar_transicion(estado_actual, nuevo_estado, roles_usuario)` con error semántico por cada caso de fallo
- [x] 4.3 Implementar método `avanzar_estado(pedido_id, nuevo_estado, usuario_actual)` con validación FSM + rol + historial + actualización
- [x] 4.4 Implementar método `cancelar_pedido(pedido_id, motivo, usuario_actual)` con validación, rollback de stock, historial

## 5. Router — Nuevos Endpoints

- [x] 5.1 Implementar `PATCH /api/v1/pedidos/{id}/estado` con dependencia de auth y `AvanzarEstadoRequest`
- [x] 5.2 Implementar `DELETE /api/v1/pedidos/{id}` con query param `motivo` para cancelación
- [x] 5.3 Implementar `GET /api/v1/pedidos/{id}` que retorna `PedidoRead` con historial incluido
- [x] 5.4 Implementar `GET /api/v1/pedidos/` con filtros opcionales y paginación
- [x] 5.5 Implementar `GET /api/v1/pedidos/{id}/historial` que retorna array de `HistorialEstadoRead`

## 6. Frontend Types y API

- [x] 6.1 Actualizar `frontend/src/entities/pedidos/types.ts`: sincronizar `PedidoCreate` con `forma_pago_codigo`, `PedidoRead` con `estado_actual` e `historial_estados`
- [x] 6.2 Agregar tipos `AvanzarEstadoRequest`, `HistorialEstadoRead` en types.ts
- [x] 6.3 Implementar funciones `avanzarEstado`, `cancelarPedido`, `getPedido`, `listarPedidos`, `getHistorialPedido` en `api.ts`
