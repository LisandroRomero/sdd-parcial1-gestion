## Why

El módulo `ingredientes` tiene modelo y schemas definidos pero carece de implementación funcional: `repository.py`, `service.py` y `router.py` están vacíos. Sin esta capa el catálogo de productos no puede exponer información de ingredientes ni alérgenos, y el Gestor de Stock no puede gestionar el maestro de ingredientes — bloqueando la personalización de pedidos (US-030, RN-CR04, RN-CR05).

## What Changes

- Implementar `IngredienteRepository` con filtro `es_alergeno` y paginación.
- Implementar `IngredienteService` con validación de unicidad de nombre y soft delete.
- Implementar `IngredienteRouter` con los endpoints CRUD del maestro de ingredientes.
- Agregar campo `deleted_at` al modelo `Ingrediente` (soft delete — actualmente ausente).
- Agregar migración Alembic para `ingrediente.deleted_at`.
- Registrar el router en `main.py`.

## Capabilities

### New Capabilities
- `ingredient-management`: CRUD del maestro de ingredientes (`GET/POST/PUT/DELETE /api/v1/ingredientes`) con filtro por `es_alergeno`, paginación estándar y soft delete. Accesible por ADMIN y STOCK.

### Modified Capabilities
- `database-models`: el modelo `Ingrediente` suma la columna `deleted_at TIMESTAMPTZ NULL` para soft delete consistente con el resto del sistema.

## Impact

- **Backend:** `backend/ingredientes/` — `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
- **Alembic:** nueva migración en `alembic/versions/`
- **App:** `backend/main.py` — registro del router `/api/v1/ingredientes`
- **Dependencias futuras:** Epic 2.3 (producto-management) necesita `IngredienteRepository` para asociar ingredientes a productos
