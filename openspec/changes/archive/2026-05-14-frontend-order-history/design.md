## Context

El epic de Órdenes tiene la mayoría de su funcionalidad implementada (5.1–5.5). Las pages `PedidoListPage` y `PedidoDetailPage` existen con filtros, paginación, timeline y cancelación. Quedan tres gaps concretos no cubiertos por los changes anteriores:

1. `OrderCard` no muestra cantidad de ítems — US-049 requiere "cantidad de ítems" en el listado
2. `PedidoDetailPage` no muestra la dirección de entrega — US-050 requiere "dirección snapshot"
3. `OrderFilters` no tiene búsqueda por número de pedido o nombre de cliente — US-051 para Gestor
4. Título de `PedidoListPage` es hardcoded "Pedidos" en lugar de adaptarse al rol del usuario

Los cambios son **exclusivamente aditivos**: no hay migraciones de BD, no se rompen interfaces existentes.

## Goals / Non-Goals

**Goals:**
- Agregar `cantidad_items` a `PedidoRead` y mostrarlo en `OrderCard`
- Agregar `DireccionSnapshot` a `PedidoDetail` y renderizarla en `PedidoDetailPage`
- Agregar query param `buscar` a `GET /pedidos` para búsqueda por ID o cliente
- Hacer el título de `PedidoListPage` role-aware ("Mis Pedidos" / "Pedidos")

**Non-Goals:**
- Pago, webhooks, reintentos (Epic 6)
- Panel admin de pedidos (7.4)
- Nuevas transiciones de estado FSM
- True address snapshot (guardar campos de dirección en la tabla `Pedido`)

## Decisions

### D1: `cantidad_items` — computed en Python vs COUNT en SQL

**Decisión:** `@computed_field` en `PedidoRead` usando `len(pedido.detalles)`. El repositorio carga `detalles` con `selectinload` en la query del listado.

**Alternativa descartada:** `COUNT(detalles)` como subconsulta — más complejo, sin ganancia para volúmenes esperados con page_size=20.

**Trade-off aceptado:** El listado carga `detalles` aunque no los muestre completos — overhead controlado por el tamaño de página.

### D2: `direccion` — JOIN a DireccionEntrega vs true snapshot

**Decisión:** `selectinload(Pedido.direccion)` en el query del detalle. El `PedidoDetail` expone un `DireccionSnapshot` con los campos de `DireccionEntrega`.

**Alternativa descartada:** Copiar campos de dirección a la tabla `Pedido` al momento de creación — requiere migración Alembic significativa y redundancia de datos.

**Trade-off aceptado:** Si el usuario edita su dirección, el detalle mostrará la versión actual. El soft delete de `DireccionEntrega` preserva la fila, así que la integridad referencial no se rompe.

### D3: `buscar` — filtro en SQL con `ilike`

**Decisión:** El param `buscar` aplica `ilike` sobre `cast(Pedido.id, String)` para buscar por número de pedido. Para GESTOR/ADMIN se agrega un JOIN a `Usuario` y busca además por `nombre` o `apellido`.

**Alternativa descartada:** Filtro post-query en Python — ineficiente cuando hay paginación.

### D4: Alcance de `buscar` por rol

**Decisión:** El param está disponible para todos los roles autenticados. Para CLIENTE, el filtro `usuario_id` ya acota los resultados a sus propios pedidos. Sin lógica de rol adicional en el query param.

## Risks / Trade-offs

- **[Overhead en listado]** Cargar `detalles` para `cantidad_items` en listas de 20 ítems → bajo impacto; `pedido_id` indexado por FK.
- **[Dirección mutable]** La dirección mostrada en el detalle puede diferir si el usuario la modificó → aceptado para el scope del parcial; true snapshot requeriría migración de BD.
- **[Sin migración Alembic]** Cambios solo en schemas Pydantic y queries ORM → cero riesgo de migración.
