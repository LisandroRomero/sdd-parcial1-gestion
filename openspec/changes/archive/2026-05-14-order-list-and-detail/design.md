## Context

El módulo de pedidos está operativo: backend completo con 6 endpoints, FSM implementada, UoW con manejo atómico de stock. El frontend tiene la página de detalle individual (`PedidoDetailPage`), el timeline de historial, y el modal de cancelación. Sin embargo, **no existe una página de listado de pedidos**. Los usuarios CLIENTE no pueden ver "Mis Pedidos", y los ADMIN/GESTOR_PEDIDOS no tienen una vista consolidada.

El backend ya expone `GET /api/v1/pedidos/` con filtro por `estado` y paginación `limit/offset`, y `GET /api/v1/pedidos/{id}` con detalle completo. El schema actual `PedidoRead` incluye `detalles` e `historial_estados` en ambos endpoints, siendo más pesado de lo necesario para el listado.

Este diseño cubre el frontend de listado y la separación de schemas backend, alineando la paginación con la especificación del integrador.

## Goals / Non-Goals

**Goals:**
- Crear página de listado de pedidos con cards responsive y paginación
- Proveer filtros por estado y rango de fechas
- Separar `PedidoRead` (compacto para listados) de `PedidoDetail` (completo para detalle)
- Migrar paginación de `limit/offset` a `page/size` con metadata (`total`, `page`, `size`, `pages`)
- Agregar ruta `/mis-pedidos` para CLIENTE y `/pedidos` para ADMIN/GESTOR_PEDIDOS
- Agregar entrada "Mis Pedidos" en la navegación del cliente

**Non-Goals:**
- No se modifica la FSM ni las transiciones de estado
- No se modifican los endpoints de cancelación ni avance de estado
- No se implementa el historial de estados del lado del frontend (ya existe en detalle)
- No se implementa la página de administración avanzada de pedidos (change 7.4)
- No se modifica el sistema de pagos ni webhooks

## Decisions

### D1: Separar schemas en `PedidoRead` (compacto) y `PedidoDetail` (completo)
- **Opción A (elegida)**: Dos schemas separados. `PedidoRead` solo incluye `id`, `estado_actual`, `total`, `subtotal`, `costo_envio`, `created_at`. `PedidoDetail` extiende `PedidoRead` agregando `detalles: list[DetallePedidoRead]`, `historial_estados`, y `pago`.
- **Opción B**: Un solo schema con campos opcionales. Más simple pero inconsistente — el contrato de la API no deja claro qué esperar.
- **Rationale**: Claridad en el contrato API. El frontend sabe exactamente qué datos tiene en cada vista. Además, el integrador ya diferencia ambos conceptos.

### D2: Paginación `page/size` con metadata
- **Opción A (elegida)**: Migrar a `page` (1-indexed), `size`, respuesta con `{ items, total, page, size, pages }`.
- **Opción B**: Mantener `limit/offset`. Es más flexible pero la especificación del integrador pide `page/size`.
- **Rationale**: Alineación con la especificación técnica (Integrador.txt). Consistencia con el resto del sistema si otros módulos adoptan el mismo formato.

### D3: Componentes de listado con diseño cards (no tabla)
- **Opción A (elegida)**: Cards con badge de estado, monto, fecha y acción rápida. Responsive por diseño.
- **Opción B**: Tabla tradicional. Funciona bien en desktop pero es problemática en mobile para la cantidad de campos de un pedido.
- **Rationale**: UX superior en mobile. Las cards permiten mostrar estado visual (colores), precio, y acciones sin comprimir columnas.

### D4: Los filtros se aplican client-side vs server-side
- **Opción A (elegida)**: Filtros server-side (query params a la API). El estado y fechas se envían como parámetros.
- **Opción B**: Filtros client-side. Más rápido en primera carga pero no escala con miles de pedidos.
- **Rationale**: El backend ya soporta filtro por `estado`. Agregar filtro por fecha es incremental. Server-side es la opción correcta para datos paginados.

### D5: Ruta unificada `/pedidos` con diferenciación por rol
- **Opción A (elegida)**: Una sola ruta `/pedidos` protegida. El componente detecta el rol del usuario y decide si lista "mis pedidos" (CLIENTE) o "todos" (ADMIN/GESTOR_PEDIDOS).
- **Opción B**: Rutas separadas `/mis-pedidos` y `/admin/pedidos`. Más explícito pero duplica lógica de ruteo.
- **Rationale**: Menos duplicación. El rol se puede obtener del store de auth y el backend ya discrimina por rol.

## Risks / Trade-offs

- **[R1] Backward compatibility de paginación**: Cambiar de `limit/offset` a `page/size` es un breaking change para consumidores existentes de la API.
  - *Mitigación*: Mantener ambos parámetros por un período de transición. El nuevo endpoint acepta `page/size` y el viejo `limit/offset` sigue funcionando (deprecado).
  
- **[R2] Schema `PedidoDetail` necesita datos de pago**: El modelo `Pedido` tiene relación con `Pago` pero el schema actual no lo serializa. Puede que el schema de pago no tenga toda la información requerida.
  - *Mitigación*: Revisar el módulo de pagos y definir un schema mínimo `PagoResumen` para incluir en el detalle.

- **[R3] Rendimiento en listado con muchos pedidos**: Si un usuario tiene miles de pedidos, el listado paginado debe ser eficiente.
  - *Mitigación*: La paginación `page/size` con `COUNT` + `LIMIT/OFFSET` (traducido internamente) es adecuada. Agregar índice compuesto en `Pedido(usuario_id, created_at)`.

- **[R4] Filtro por fecha requiere cambios en backend**: Actualmente el listado no soporta filtro por rango de fechas.
  - *Mitigación*: Agregar query params `fecha_desde` y `fecha_hasta` en el endpoint GET `/pedidos/`. Cambio menor en repository y router.
