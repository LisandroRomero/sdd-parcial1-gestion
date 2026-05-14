## Why

El módulo de pedidos actualmente solo soporta la creación de pedidos (estado `PENDIENTE`). Toda la lógica de la Máquina de Estados Finitos (FSM) de 6 estados definida en la especificación —transiciones válidas, validación de estado terminal, cancelación con motivo obligatorio, roles autorizados por transición, y audit trail completo— está sin implementar. Sin esta funcionalidad el sistema no puede procesar el ciclo de vida completo de un pedido: confirmar, preparar, enviar, entregar o cancelar. Además, los códigos de estado en el seed (`PREPARACION`, `ENVIADO`) están desalineados con la spec (`EN_PREP`, `EN_CAMINO`), lo que causaría fallos en cualquier lógica de validación futura.

## What Changes

- **FSM engine**: Implementar `avanzar_estado()` y `cancelar_pedido()` en `pedidos/service.py` con un mapa explícito de transiciones válidas y validación de estado terminal
- **Role-guarded transitions**: Validar que el rol del usuario autenticado tenga permiso para ejecutar cada transición específica (CLIENTE solo puede cancelar desde PENDIENTE, ADMIN puede cancelar desde cualquier no-terminal, GESTOR_PEDIDOS maneja las transiciones del flujo normal)
- **Endpoint `PATCH /api/v1/pedidos/{id}/estado`**: Para avanzar al siguiente estado en el flujo
- **Endpoint `DELETE /api/v1/pedidos/{id}`**: Cancelar pedido con motivo obligatorio
- **Endpoint `GET /api/v1/pedidos/{id}`**: Obtener detalle del pedido con historial de estados incluido
- **Endpoint `GET /api/v1/pedidos/`**: Listar pedidos del usuario autenticado (con filtros opcionales)
- **Endpoint `GET /api/v1/pedidos/{id}/historial`**: Obtener el audit trail completo del pedido
- **`HistorialEstadoPedido`**: Agregar campos `usuario_id` (quién ejecutó la transición, nullable para sistema) y `motivo` (obligatorio si el nuevo estado es CANCELADO)
- **Schema `AvanzarEstadoRequest`**: Reemplazar el `estado_actual` mutable de `PedidoUpdate` por un schema DTO dedicado con `nuevo_estado` y `motivo` opcional
- **Seed alignment**: Renombrar `PREPARACION → EN_PREP` y `ENVIADO → EN_CAMINO` en el seed de `EstadoPedido` y en `es_terminal` flags
- **`PedidoCreate`**: Agregar campo `forma_pago_codigo` obligatorio
- **Frontend types sync**: Actualizar `frontend/src/entities/pedidos/types.ts` para reflejar los cambios (incluir nuevas interfaces para AvanzarEstadoRequest, estado history, endpoints)

## Capabilities

### New Capabilities
- `order-state-machine`: Lógica completa de la FSM de pedidos — transiciones válidas, validación de roles por transición, guardas de estado terminal, cancelación con motivo obligatorio, y endpoints REST para el ciclo de vida del pedido (avanzar, cancelar, consultar, historial)

### Modified Capabilities
- `order-creation`: Agregar `forma_pago_codigo` como campo obligatorio en `PedidoCreate` y actualizar schemas y frontend types para reflejar la sincronización

## Impact

- **Backend**: `backend/pedidos/` — cambios en `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`; nueva migración Alembic para `HistorialEstadoPedido.usuario_id` y `HistorialEstadoPedido.motivo`
- **Seed**: `backend/scripts/seed.py` — renombrar códigos de estado y ajustar `es_terminal`
- **Frontend**: `frontend/src/entities/pedidos/` — actualizar `types.ts`, agregar funciones API en `api.ts`; componentes que usen `estado` deben migrar a `estado_actual`
- **Auth**: Las dependencias de autorización por rol (`RoleChecker`) deben integrarse en los nuevos endpoints de pedidos
