## Contexto

El historial de cambios de estado (`HistorialEstadoPedido`) ya está completamente implementado en backend:

- **Modelo** (`pedidos/model.py:79-103`): SQLModel con FK a `pedido`, `estadopedido` (desde/hasta), `usuario`, más `motivo` y `created_at`
- **Schema** (`pedidos/schemas.py:73-82`): `HistorialEstadoRead` con `from_attributes=True`
- **Escritura** (`pedidos/service.py`): cada transición (`crear_pedido:128-133`, `avanzar_estado:194-201`, `cancelar_pedido:249-256`) inserta un registro vía `uow.session.add()`
- **Lectura en BD** (`pedidos/repository.py:58-65`): `PedidoRepository.get_historial(pedido_id)` con ORDER BY `created_at ASC`
- **Endpoint** (`pedidos/router.py:170-185`): `GET /{id}/historial` existe pero **sin autorización** — cualquier usuario autenticado obtiene el historial de cualquier pedido

**Frontend**:
- `PedidoDetailPage.tsx` ya renderiza un timeline inline (líneas 169-209) hardcodeado en el JSX, sin componente extraíble
- El API client (`entities/pedidos/api.ts:19-20`) ya expone `getHistorialPedido`
- Los tipos TypeScript (`entities/pedidos/types.ts:40-48`) ya definen `HistorialEstadoRead`

**Validación de motivo**: `cancelar_pedido` (service.py:230-231) ya valida que `motivo` no sea vacío. No requiere cambios.

---

## Goals / Non-Goals

**Goals:**

- Agregar guard de autorización al endpoint `GET /{id}/historial` usando el mismo patrón que `get_pedido` (router.py:128-131)
- Extraer componente `OrderTimeline` en `entities/pedidos/ui/OrderTimeline/` como widget reutilizable de dominio, reemplazando el timeline inline actual
- Agregar tests de backend: autorización (CLIENT no puede ver historial ajeno, ADMIN/PEDIDOS sí), 404 para pedido inexistente, integridad de datos devueltos

**Non-Goals:**

- No se modifica el modelo ni el schema (`HistorialEstadoPedido` ya cumple RN-03 append-only, RN-02 primer entrada con `estado_desde = NULL`)
- No se extrae `HistorialEstadoPedidoRepository` dedicado — `session.add()` directo en service es aceptable para writes append-only y el `get_historial` ya vive en `PedidoRepository`
- No se agregan nuevos endpoints ni nuevas transiciones de estado
- No se toca la validación de `motivo` (ya implementada)

---

## Decisiones

### D01 — Guard de autorización (backend)

El patrón exacto ya existe en `get_pedido` (router.py:128-131):

```python
user_roles = {ur.rol_codigo for ur in current_user.roles}
if "CLIENT" in user_roles and len(user_roles) == 1 and pedido.usuario_id != current_user.id:
    raise ForbiddenException("PEDIDO_NO_AUTORIZADO")
```

Se replica idéntico en `get_historial_pedido` después del `NotFoundException`. La lógica:

- **CLIENT puro** (único rol `CLIENT`): solo ve historial de sus propios pedidos (`pedido.usuario_id == current_user.id`)
- **ADMIN / GESTOR_PEDIDOS** (con o sin rol CLIENT adicional): ve cualquier historial
- `len(user_roles) == 1` evita falsos positivos cuando un admin también tiene rol CLIENT

No se necesita un guard a nivel service porque el historial no tiene lógica de negocio propia — es una consulta de solo lectura. El guard en router es suficiente y consistente con el resto del módulo.

### D02 — Sin repositorio dedicado de historial

El service actual escribe historial con `uow.session.add(historial)` en lugar de usar un repositorio. Extraer `HistorialEstadoPedidoRepository` requeriría:

- Crear clase que herede `BaseRepository[HistorialEstadoPedido]`
- Registrar `historial_estados` en `_get_uow()` (router.py)
- Modificar 3 lugares en service (`crear_pedido`, `avanzar_estado`, `cancelar_pedido`) para usar `uow.repos.historial_estados.create(historial)` en vez de `session.add()`

**Decisión**: No se hace. Razones:

- `HistorialEstadoPedido` es append-only (RN-03): no hay updates, no hay deletes, no hay queries complejas
- La operación de escritura es trivial (`INSERT INTO ...`)
- El `get_historial` ya está en `PedidoRepository` que es donde tiene sentido (depende de un `pedido_id`)
- El refactor agrega complejidad sin beneficio medible

Si en el futuro aparecen queries complejas (reportes, agregaciones), se extrae en ese momento.

### D03 — OrderTimeline recibe `historial` como prop

El timeline recibe `historial: HistorialEstadoRead[]` como prop. La página de detalle le pasa `pedido.historial_estados` (que ya viene en la respuesta de `GET /pedidos/{id}`).

No se usa `getHistorialPedido` (el endpoint dedicado) en la página porque:

- Ya tenemos los datos en `pedido.historial_estados` — agregar otra petición es una regresión de performance
- El endpoint dedicado existe para casos de uso donde no se tiene el pedido completo (ej: widget embebido, panel de auditoría)
- Si el componente necesita refrescar solo el timeline sin recargar todo el pedido en el futuro, se puede agregar un `useQuery` paralelo sin cambiar la interfaz del componente

### D04 — Ubicación: `entities/pedidos/ui/OrderTimeline/`

FSD estricto: el timeline es un widget de visualización de una entidad de dominio, no contiene lógica de negocio ni mutación. Le corresponden las capas:

```
shared/ui/   → no, es específico de pedidos
features/    → no, no tiene lógica de negocio ni interacción compleja
entities/    → sí, es presentación visual pura de una entidad de dominio
```

Estructura:

```
entities/pedidos/
├── ui/
│   └── OrderTimeline/
│       ├── OrderTimeline.tsx      ← componente principal
│       └── index.ts               ← re-export
├── api.ts
├── types.ts
└── index.ts
```

### D05 — Estados y visuales (frontend)

Se reutiliza el `statusColors` y `statusLabels` que ya existen en `PedidoDetailPage.tsx` (líneas 10-26). Se mueven a un archivo compartido dentro de `entities/pedidos/` o se definen como constantes locales del componente. El timeline vertical muestra:

- **Círculo con color** del estado destino (`estado_hasta`), usando `statusColors`
- **Línea vertical** conectando entradas consecutivas
- **Nombre del estado** en español (de `statusLabels`)
- **Transición**: "desde {estado_desde}" si no es la primera entrada (RN-02)
- **Timestamp** formateado con `DateTimeFormat('es-AR', { dateStyle: 'long', timeStyle: 'short' })`
- **Usuario responsable**: si `usuario_id` está presente, mostrar nombre (opcional en primera iteración)
- **Motivo**: si `motivo` no es null, mostrarlo en texto secundario

### D06 — Tests (backend)

Archivo nuevo: `backend/tests/test_pedidos_historial.py`

Tres escenarios:

1. **Autorización — CLIENT ve su propio historial**: crear pedido como CLIENT, llamar `GET /{id}/historial` → 200 con datos correctos
2. **Autorización — CLIENT no ve historial ajeno**: crear pedido como CLIENT A, llamar `GET /{id}/historial` como CLIENT B → 403 Forbidden
3. **Autorización — ADMIN/PEDIDOS ve cualquier historial**: crear pedido como CLIENT, llamar `GET /{id}/historial` como ADMIN o GESTOR_PEDIDOS → 200
4. **404**: llamar `GET /99999/historial` → 404 NotFound
5. **Integridad de datos**: verificar que los campos devueltos coinciden con lo insertado (orden cronológico, `estado_desde = NULL` en primer entry, `estado_hasta`, `motivo`)

---

## Riesgos / Trade-offs

- **El endpoint dedicado `getHistorialPedido` queda sin uso en frontend por ahora**. Si bien existe y está autorizado, el frontend consume los datos del pedido completo. Esto significa que bugs en el endpoint no se detectan hasta que alguien lo use directamente (ej: herramientas de debugging, futura feature de auditoría). Mitigación: los tests de integración cubren el endpoint.
- **`session.add()` directo en service**: es un desvío del patrón Repository, pero la decisión D02 explica por qué es aceptable acá. Si alguien nuevo llega al código, puede preguntarse por qué no hay un repo de historial. El `design.md` (este archivo) queda como registro de la decisión.
- **Mover `statusColors`/`statusLabels`**: actualmente definidos en `PedidoDetailPage.tsx` y también en `CancelarPedidoModal.tsx` (probablemente). Al extraerlos a un módulo compartido en `entities/pedidos/`, rompemos imports en dos lugares. Es un refactor pequeño pero hay que hacerlo.
