## Why

No existe un panel de administración de catálogo en el frontend. ADMIN necesita poder crear, editar y eliminar productos, categorías e ingredientes sin depender del Gestor de Stock. Adicionalmente, los endpoints `POST/PUT/DELETE /productos` tienen `require_role("ADMIN")` pero omiten el rol `STOCK`, bloqueando a gestores de stock de crear/editar/eliminar productos (bug de RBAC).

## What Changes

- **Backend — fix guards en productos**: agregar `"STOCK"` a `require_role` en los endpoints `POST /productos/`, `PUT /productos/{id}`, `DELETE /productos/{id}` (actualmente solo ADMIN, falta STOCK)
- **Frontend — tipos admin**: extender `entities/producto/types.ts` y crear tipos para mutaciones (ProductoCreate, ProductoUpdate, StockUpdate, CategoriaCreate, CategoriaUpdate, IngredienteCreate, IngredienteUpdate)
- **Frontend — API clients admin**: funciones de creación, edición y eliminación para productos, categorías e ingredientes
- **Frontend — hooks**: hooks TanStack Mutation para cada operación
- **Frontend — páginas admin**:
  - `AdminProductosPage` — tabla de todos los productos (activos y soft-deleted), crear, editar, cambiar stock, eliminar
  - `AdminCategoriasPage` — tabla de categorías con jerarquía, crear, editar, eliminar
  - `AdminIngredientesPage` — tabla de ingredientes con flag alergeno, crear, editar, eliminar
- **Frontend — routing**: rutas `/admin/productos`, `/admin/categorias`, `/admin/ingredientes` bajo `AdminRoute`

## Capabilities

### New Capabilities

- `admin-product-catalog`: Panel admin para gestión completa de productos — listado con soft-deleted, CRUD, stock update, eliminación lógica.
- `admin-category-management-panel`: Panel admin para categorías — listado con jerarquía (parent), CRUD, soft delete.
- `admin-ingredient-management-panel`: Panel admin para ingredientes — listado con flag alergeno, CRUD, soft delete.

### Modified Capabilities

- `product-crud-and-stock`: Los endpoints `POST/PUT/DELETE /productos` deben aceptar rol STOCK además de ADMIN — corrección de RBAC omitido en la implementación original.

## Impact

**Backend:**
- `backend/productos/router.py` — cambiar 3 guards de `require_role("ADMIN")` a `require_role("ADMIN", "STOCK")`

**Frontend:**
- `frontend/src/entities/producto/types.ts` — agregar interfaces de creación/actualización para productos
- `frontend/src/entities/admin/types.ts` — agregar interfaces para categorías e ingredientes admin
- `frontend/src/features/admin/api/adminProductosApi.ts` — crear, actualizar, eliminar, stock
- `frontend/src/features/admin/api/adminCategoriasApi.ts` — crear, actualizar, eliminar
- `frontend/src/features/admin/api/adminIngredientesApi.ts` — crear, actualizar, eliminar
- `frontend/src/features/admin/hooks/` — hooks de mutación para cada entidad
- `frontend/src/pages/admin/AdminProductosPage.tsx` — página nueva
- `frontend/src/pages/admin/AdminCategoriasPage.tsx` — página nueva
- `frontend/src/pages/admin/AdminIngredientesPage.tsx` — página nueva
- `frontend/src/app/router.tsx` — 3 nuevas rutas admin
