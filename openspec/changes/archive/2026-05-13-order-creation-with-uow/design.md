## Context

El sistema ya tiene implementado el patrón `Router → Service → UoW → Repository → Model` en categorías, ingredientes, y productos. El `UnitOfWork` gestiona sesiones SQLAlchemy, expone un `_ReposRegistry` con lazy init, y garantiza rollback automático ante excepciones no-HTTP. Los modelos `Pedido` y `DetallePedido` (también llamado `DetallePedido` en el modelo actual, donde el campo es `detalles`) ya están definidos en `backend/pedidos/model.py`, pero `service.py` y `repository.py` están vacíos.

**Estado actual de `backend/pedidos/`:**

| Archivo | Estado |
|---|---|
| `model.py` | Completo: `Pedido`, `DetallePedido`, `EstadoPedido`, `HistorialEstadoPedido` |
| `schemas.py` | Parcial: `PedidoCreate` incluye `usuario_id` (no debe venir del body) y `forma_pago_codigo` (no requerido en este epic) |
| `repository.py` | Vacío |
| `service.py` | Vacío |
| `router.py` | Vacío |

**Observación clave sobre el modelo existente**: `Pedido.estado_actual` es FK a tabla `estadopedido` (string código), y `Pedido.forma_pago_codigo` es FK a tabla `formapago`. Para este epic, el cliente no elige forma de pago al crear (eso pertenece al epic de pagos). Necesitamos un valor placeholder o hacer la columna opcional.

## Goals / Non-Goals

**Goals:**

- Implementar `POST /api/v1/pedidos` con transacción all-or-nothing
- Snapshot de precios en `DetallePedido.nombre_snapshot` y `precio_snapshot`
- Validación de stock y descuento atómico dentro de la misma sesión
- Verificación de ownership de `DireccionEntrega`
- Restricción de rol a `CLIENTE`
- Registrar repos en `core/dependencies.py`

**Non-Goals:**

- Integración con pagos (MercadoPago) — Epic de pagos
- FSM de transiciones de estado (PENDIENTE → CONFIRMADO etc.) — Epic de gestión de pedidos
- Notificaciones al gestor de pedidos — Epic de gestión de pedidos
- Listar / cancelar pedidos — Epics posteriores
- `HistorialEstadoPedido` en esta transacción (puede ser vacío para creación inicial o con entrada `PENDIENTE`)

## Decisions

### D1: `usuario_id` viene del JWT, no del body

El `PedidoCreate` actual incluye `usuario_id` en el body. Esto es un bug de diseño: el usuario autenticado NO debe poder especificar el `usuario_id` de otro usuario.

**Decisión**: el `PedidoCreate` del endpoint solo acepta `direccion_id: int` y `detalles: list[DetallePedidoCreate]`. El service recibe `current_user: Usuario` como parámetro separado.

**Alternativa rechazada**: validar que `body.usuario_id == current_user.id` — innecesariamente frágil y permite que alguien teste con IDs distintos.

### D2: `forma_pago_codigo` en Pedido — placeholder vacío

El modelo tiene `Pedido.forma_pago_codigo: str` con FK a `formapago`. El epic de pagos asigna la forma de pago. Opciones:

1. Hacer la columna nullable (requiere migración)
2. Usar un string placeholder `"PENDIENTE"` (sin FK real)
3. Eliminar la FK por ahora

**Decisión**: hacer `forma_pago_codigo` nullable en el modelo y migración. El endpoint de creación lo deja en `None`. Cuando el epic de pagos complete la transacción, llena esta columna.

**Alternativa rechazada**: placeholder string — viola integridad referencial si la tabla `formapago` no tiene ese registro.

### D3: Descuento de stock con SELECT FOR UPDATE

Si dos requests concurrentes compran el mismo producto con stock = 1, ambos podrían pasar la validación y dejar stock en -1.

**Decisión**: usar `select(Producto).where(Producto.id == id).with_for_update()` al cargar productos para validación+descuento. Esto es un row-level lock dentro de la transacción SQLAlchemy.

**Alternativa rechazada**: `stock_cantidad >= 0` constraint en BD + manejo de IntegrityError — más complejo de razonar y da peor UX (500 en vez de 422 descriptivo).

### D4: Registro de repos en `get_uow` (dependencies.py)

Los repos de pedidos, productos y direcciones deben estar disponibles en el UoW del endpoint.

**Decisión**: agregar en `_register_repos()`:
- `"pedidos"` → `PedidoRepository`
- `"detalles_pedido"` → `DetallePedidoRepository`
- `"productos"` → `ProductoRepository` (ya implementado)
- `"direcciones"` → `DireccionEntregaRepository`

**Nota**: `ProductoRepository` y `DireccionEntregaRepository` ya existen; solo hay que importarlos y registrarlos.

### D5: Atomicidad — una sola llamada a `uow.commit()`

Todo el flujo de creación (validar dirección, cargar productos, validar stock, crear Pedido, crear DetallesPedido, descontar stock) ocurre dentro de la misma sesión antes de un único `uow.commit()` en el router.

Si cualquier excepción (incluida `ValidationException`) escapa del service, el `get_uow` dependency hace rollback automático, cancelando todos los `session.flush()` intermedios.

### D6: Manejo del modelo `EstadoPedido`

La tabla `estadopedido` existe y tiene FK desde `Pedido`. El estado inicial `"PENDIENTE"` debe existir como registro seed.

**Decisión**: asumir que el seed de estados está hecho (Epic 0.4 base-patterns-backend). El service asigna `estado_actual="PENDIENTE"` directamente.

### D7: `HistorialEstadoPedido` en creación

El modelo tiene una tabla de auditoría de estados.

**Decisión**: al crear el pedido, insertar una entrada de historial con `estado_desde=None` y `estado_hasta="PENDIENTE"`. Esto mantiene el audit trail completo desde el primer momento.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Deadlocks con `SELECT FOR UPDATE` en alta concurrencia | Siempre adquirir locks en orden ascendente de `producto_id` para evitar deadlock circular |
| `forma_pago_codigo` nullable rompe constraints futuros | Documentar que el epic de pagos DEBE llenar este campo; agregar validación en el FSM de estados que no permita avanzar a CONFIRMADO sin forma de pago |
| `stock_cantidad` puede bajar a 0 pero nunca a negativo si se usa FOR UPDATE | Constraint `CHECK (stock_cantidad >= 0)` en migración como segunda línea de defensa |
| Schemas `PedidoCreate`/`PedidoRead` en `schemas.py` no coinciden con el diseño | Refactorizar `schemas.py` como parte de este epic |

## Migration Plan

1. Generar migración Alembic con `alembic revision --autogenerate -m "make_forma_pago_nullable_pedido"`
2. Modificar columna `forma_pago_codigo` a nullable
3. Agregar constraint `CHECK (stock_cantidad >= 0)` en tabla `producto` (si no existe)
4. Seed de `estadopedido` con `PENDIENTE`, `CONFIRMADO`, etc. (verificar si ya existe)
5. Deploy: las tablas `pedido` y `detallepedido` deben crearse si no existen (verificar con `alembic current`)

## Open Questions

- ¿El `costo_envio` en `Pedido` se calcula en este epic o siempre es 0? → Asumir `0.00` por ahora; el epic de envíos lo calcula.
- ¿El seed de `estadopedido` ya fue aplicado en Epic 0.4? → Verificar antes de correr la migración.
- ¿`formapago` seed existe? → Si `forma_pago_codigo` queda nullable, no importa para este epic.
