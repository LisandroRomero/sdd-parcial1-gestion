## Context

El módulo `backend/pedidos/` actualmente implementa solo la creación de pedidos. El `Pedido` se crea con `estado_actual = "PENDIENTE"` y se guarda el historial inicial en `HistorialEstadoPedido`. No existe ninguna lógica para transicionar entre los 6 estados definidos en la especificación: `PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO`, más `CANCELADO` como estado terminal accesible desde cualquier no-terminal.

El `HistorialEstadoPedido` carece de `usuario_id` y `motivo`, el seed usa códigos de estado desalineados con la spec, y no hay validación por roles en las transiciones. Además, `PedidoCreate` no recibe `forma_pago_codigo` y el frontend tiene tipos desincronizados.

Esta implementación impacta: `backend/pedidos/` (model, schemas, repository, service, router), `backend/scripts/seed.py`, migraciones Alembic, y `frontend/src/entities/pedidos/`.

## Goals / Non-Goals

**Goals:**
- Implementar el motor FSM con mapa explícito de transiciones válidas en `pedidos/service.py`
- Exponer endpoints REST para el ciclo de vida: avanzar estado, cancelar, consultar detalle con historial, listar pedidos
- Completar `HistorialEstadoPedido` con `usuario_id` y `motivo` (migración Alembic)
- Validar roles por transición según la especificación (CLIENTE, ADMIN, GESTOR_PEDIDOS)
- Alinear códigos de estado del seed con la spec (`EN_PREP`, `EN_CAMINO`)
- Agregar `forma_pago_codigo` a `PedidoCreate`
- Sincronizar tipos del frontend con los schemas del backend

**Non-Goals:**
- NO incluye la integración con webhooks de MercadoPago para la transición `PENDIENTE → CONFIRMADO` (se implementa en change separado de pagos)
- NO incluye UI de frontend para la gestión de pedidos (pantalla de "mis pedidos", panel de gestión) — solo tipos y API functions
- NO incluye rate limiting en los nuevos endpoints
- NO incluye notificaciones al cambiar de estado

## Decisions

### D1. Mapa de transiciones como `dict` inmutable en service

**Decisión:** Definir `TRANSICIONES_VALIDAS` como un `dict` anidado `{estado_origen: {estado_destino: set[RolesPermitidos]}}` dentro de `service.py`.

| Desde | Hacia | Roles |
|-------|-------|-------|
| PENDIENTE | CONFIRMADO | `{SISTEMA}` (reservado para webhook MP) |
| PENDIENTE | CANCELADO | `{CLIENTE, ADMIN, GESTOR_PEDIDOS}` |
| CONFIRMADO | EN_PREP | `{GESTOR_PEDIDOS}` |
| CONFIRMADO | CANCELADO | `{ADMIN, GESTOR_PEDIDOS}` |
| EN_PREP | EN_CAMINO | `{GESTOR_PEDIDOS}` |
| EN_PREP | CANCELADO | `{ADMIN}` |
| EN_CAMINO | ENTREGADO | `{GESTOR_PEDIDOS}` |
| ENTREGADO | — | Terminal |
| CANCELADO | — | Terminal |

**Alternativa considerada:** Tabla en BD con un modelo `TransicionEstado`. Se descartó porque el mapa es estático y pequeño (8 transiciones), no necesita persistencia ni configuración dinámica. Un dict en Python da type safety, es testeable, y evita una tabla adicional.

### D2. Servicio stateless con métodos dedicados

**Decisión:** Dos métodos públicos en `PedidoService`:

- `avanzar_estado(pedido_id, nuevo_estado, usuario_actual)` — valida transición, rol, inserta historial, actualiza pedido
- `cancelar_pedido(pedido_id, motivo, usuario_actual)` — wrapper que fuerza `nuevo_estado=CANCELADO`, requiere motivo, ejecuta rollback de stock vía repositorio de productos

Ambos métodos reciben el usuario autenticado (no solo rol) para registrar `usuario_id` en el historial.

**Alternativa considerada:** Clase `OrderFSM` separada. Se descartó por simplicidad — la lógica cabe en 50 líneas dentro del service existente y no justifica otra capa de abstracción.

### D3. Historial incluye `usuario_id` nullable + `motivo`

**Decisión:** Agregar los campos a la tabla SQLModel:

- `usuario_id: Optional[int]` — FK a `usuarios.usuario.id`, nullable para transiciones automáticas del sistema (ej: webhook)
- `motivo: Optional[str]` — nullable, pero **obligatorio por validación** cuando el destino es `CANCELADO` (RN-05)

**Alternativa considerada:** Tabla de `Cancelacion` separada. Se descartó porque el historial es el lugar natural para registrar el motivo, y una tabla extra complejifica las consultas sin beneficio real.

### D4. Seed alignment sin migración de datos

**Decisión:** Actualizar `backend/scripts/seed.py` para usar `EN_PREP` y `EN_CAMINO`. No se requiere migración porque no hay datos reales en BD (entorno de desarrollo). El `es_terminal` debe ser `False` para ambos.

**Riesgo:** Si existieran pedidos en estado `PREPARACION` o `ENVIADO` en alguna BD, romperían. Se documenta como riesgo y se mitiga con validación en el service que solo opera sobre estados conocidos.

### D5. Schema `AvanzarEstadoRequest` dedicado

**Decisión:** Crear schema Pydantic separado en vez de reusar `PedidoUpdate`:

```python
class AvanzarEstadoRequest(BaseModel):
    nuevo_estado: str
    motivo: Optional[str] = None  # requerido si nuevo_estado == "CANCELADO"
```

**Alternativa considerada:** Usar `PedidoUpdate` existente. Se descartó porque `PedidoUpdate` permite mutar otros campos (`direccion_id`, `forma_pago_codigo`) que no corresponden a una transición de estado — viola el principio de segregación de interfaces.

### D6. `forma_pago_codigo` como campo obligatorio en `PedidoCreate`

**Decisión:** Agregar el campo a `PedidoCreate`:

```python
class PedidoCreate(BaseModel):
    direccion_id: int
    forma_pago_codigo: str
    detalles: list[DetallePedidoCreate]
```

El frontend debe actualizar `PedidoCreate` para incluir `forma_pago_codigo`.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **R1 - Datos existentes con códigos viejos**: Si hay pedidos con estados `PREPARACION`/`ENVIADO` en BD, el seed alignment los deja huérfanos | El service valida contra el mapa actual; se agrega migración opcional para normalizar si hay datos reales |
| **R2 - Concurrencia en transiciones**: Dos requests simultáneas podrían avanzar el mismo pedido desde el mismo estado | El UoW maneja la transacción; usar `SELECT ... FOR UPDATE` sobre el pedido al leer antes de transicionar (mismo patrón que creación) |
| **R3 - Abuso del endpoint de cancelación**: Un CLIENTE podría cancelar repetidamente sin costo | Endpoint idempotente: si el pedido ya está cancelado, devolver `409 Conflict` con error ya existente |
| **R4 - Frontend desincronizado**: Si el frontend se actualiza antes que el backend, los tipos nuevos pueden romper | Los cambios de frontend se limitan a types y API functions; los componentes se actualizan en change separado |
| **R5 - Sin idempotencia en avanzar estado**: Llamar dos veces al mismo `avanzar_estado` desde CONFIRMADO a EN_PREP | El service valida que `estado_actual` coincida con el origen esperado; la segunda llamada recibe `409 Conflict` |

## Migration Plan

1. **Crear migración Alembic** que agregue `usuario_id` (FK → usuarios, nullable) y `motivo` (VARCHAR, nullable) a `HistorialEstadoPedido`
2. **Actualizar seed** con códigos corregidos y migración local
3. **Implementar** mapa FSM, validaciones, service methods, schemas, repository methods
4. **Implementar** endpoints REST en router
5. **Actualizar frontend types** y API functions
6. **Test** manual con curl/Postman: ciclo completo PENDIENTE → CANCELADO y PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO

**Rollback:** Revertir commit de la migración y volver al seed anterior.
