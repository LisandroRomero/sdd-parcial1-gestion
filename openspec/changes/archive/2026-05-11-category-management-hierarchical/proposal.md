## Why

El sistema tiene el modelo `Categoria` con FK auto-referencial y soft delete, pero `repository.py`, `service.py` y `router.py` están vacíos. Sin este change, el catálogo de productos no puede asignar ni navegar categorías, y los changes 2.2–2.5 (ingredientes, productos, catálogo público) no pueden implementarse.

## What Changes

- Implementar `CategoriaRepository` con query CTE recursiva para construir el árbol jerarquico de profundidad arbitraria.
- Implementar `CategoriaService` con validación de ciclos (RN-CA01 / RN-CA02) y validación de productos activos antes de soft delete (RN-CA03).
- Agregar schema `CategoriaTree` para la respuesta jerárquica anidada del endpoint público `GET /api/v1/categorias`.
- Implementar 4 endpoints REST: `POST`, `GET` (árbol público), `PUT /{id}`, `DELETE /{id}`.
- Registrar el router en `backend/main.py`.

## Capabilities

### New Capabilities
- `category-management`: CRUD de categorías jerárquicas con CTE recursiva, validación de ciclos y soft delete protegido.

### Modified Capabilities
<!-- Sin requirement changes en specs existentes -->

## Impact

- `backend/categorias/repository.py` — implementación completa (vacío actualmente)
- `backend/categorias/service.py` — lógica de negocio con validación de ciclos (vacío actualmente)
- `backend/categorias/router.py` — 4 endpoints REST (vacío actualmente)
- `backend/categorias/schemas.py` — agregar `CategoriaTree` (schema de respuesta jerárquica)
- `backend/core/uow.py` — exponer `categorias` repository via `__getattr__`
- `backend/main.py` — registrar `categorias_router` con prefijo `/api/v1`
- Sin cambios en modelo ni en migraciones Alembic (tabla ya creada en 0.3)
