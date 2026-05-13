## Context

El módulo `backend/productos/` tiene el modelo `Producto` (con `deleted_at`, `precio_base DECIMAL`, `stock_cantidad`, `disponible`) y schemas básicos ya definidos. `repository.py`, `service.py` y `router.py` están vacíos. La tabla `productocategoria` (pivot N:M) ya existe en BD con `es_principal BOOLEAN`. El patrón de `_get_uow()` local con `uow.__enter__()` + commit explícito es el establecido por `categorias/router.py`.

## Goals / Non-Goals

**Goals:**
- Implementar `ProductoRepository` con consultas activas (filtro `deleted_at IS NULL`) y gestión de pivotes `ProductoCategoria`.
- Implementar `ProductoService` con validaciones: SKU único, precio > 0, stock ≥ 0.
- Implementar `ProductoRouter` con endpoints de administración: `POST`, `PUT`, `DELETE`, `PATCH /disponibilidad`, `PATCH /stock`.
- Agregar schemas `StockUpdate`, `DisponibilidadUpdate`; extender `ProductoCreate` y `ProductoUpdate` con `categoria_ids`.
- Registrar el router en `api/v1/router.py`.

**Non-Goals:**
- `GET /api/v1/productos` (catálogo público) — change 2.5.
- `GET /api/v1/productos/{id}` (detalle público) — change 2.5.
- Endpoints de ingredientes del producto — change 2.4.
- Frontend — change 7.3.

## Decisions

### 1. Schemas: `categoria_ids` en Create y Update

**Decisión:** agregar `categoria_ids: list[int] = []` a `ProductoCreate` y `ProductoUpdate`. Todos los pivotes creados con `es_principal=False` por defecto.

**Rationale:** la spec dice explícitamente "Crear producto con ingredientes y categorías". Incluir los IDs de categorías en el body de creación es más ergonómico que un endpoint separado. Alternativa: endpoints dedicados `/productos/{id}/categorias` — innecesario para v1, genera más round-trips al cliente.

### 2. Sync de categorías en PUT (reemplazo total)

**Decisión:** en `PUT`, el service elimina **todos** los `ProductoCategoria` actuales y crea nuevos según la lista recibida. Si `categoria_ids` no está en el body (campo no enviado), se preservan los actuales.

**Rationale:** PUT semántica implica reemplazo. Alternativa: merge incremental (PATCH) — confuso para el cliente y más complejo de implementar. El reemplazo es predecible.

**Implementación en repository:**
```python
def sync_categorias(self, producto_id: int, categoria_ids: list[int]) -> None:
    # delete all existing pivots for this product
    self.session.exec(delete(ProductoCategoria).where(...))
    # insert new ones
    for cat_id in categoria_ids:
        self.session.add(ProductoCategoria(producto_id=producto_id, categoria_id=cat_id))
    self.session.flush()
```

### 3. PATCH /stock — seteo absoluto

**Decisión:** `PATCH /api/v1/productos/{id}/stock` acepta `{ stock_cantidad: int }` y **reemplaza** el valor (seteo absoluto). Validación: `stock_cantidad >= 0`.

**Rationale:** la US-021 dice "seteo absoluto o incremento". El seteo absoluto es más simple y explícito. El frontend puede calcular el nuevo valor. Alternativa: operación `+N / -N` — requiere lógica de race condition (SELECT + UPDATE). El seteo absoluto se puede hacer con un único UPDATE seguro.

### 4. Validación de categorías existentes

**Decisión:** el service verifica que cada `categoria_id` en la lista corresponda a una categoría activa antes de crear los pivotes. Lanza `HTTP 404` con lista de IDs inválidos si alguno no existe.

**Rationale:** evitar FK violations silenciosas en BD. El error 404 con detalle específico es más útil que un 500 de IntegrityError.

### 5. SKU único — validación en Service

**Decisión:** el service llama `repo.exists_by_sku(sku, exclude_id)` antes de `create()` y `update()`. Lanza `HTTP 409` si el SKU ya está en uso por otro producto activo.

**Rationale:** misma razón que en ingredientes — un IntegrityError sin tratar da 500. El constraint UNIQUE en BD actúa como segunda línea de defensa.

### 6. Integración con UoW

**Decisión:** `_get_uow()` local registra `ProductoRepository` igual que en `categorias`. El router llama `uow.commit()` explícitamente tras operaciones de escritura.

```python
uow.repos.register("productos", lambda s: ProductoRepository(s))
```

## Risks / Trade-offs

- **[Trade-off] Sync de categorías O(n) en updates frecuentes** → en un catálogo de comida con pocos productos y pocas categorías, el DELETE + INSERT es negligible. No es un riesgo operacional.
- **[Riesgo] Race condition en PATCH /stock con múltiples requests** → mitigado con un UPDATE directo en BD (no SELECT + UPDATE). SQLModel/SQLAlchemy flushea inmediatamente; el commit del UoW garantiza atomicidad.
- **[Riesgo] Categorías inválidas en `categoria_ids`** → validación explícita en service antes de sync. FK constraint en BD como segunda defensa.

## Migration Plan

1. No hay cambios de modelo ni migraciones (el modelo `Producto` ya tiene todos los campos, tabla ya existe).
2. Orden de implementación: `schemas.py` (agregar StockUpdate, DisponibilidadUpdate, categoria_ids) → `repository.py` → `service.py` → `router.py` → `api/v1/router.py`.
3. Verificar con `POST /api/v1/productos` y confirmar `201` con `id` asignado.
