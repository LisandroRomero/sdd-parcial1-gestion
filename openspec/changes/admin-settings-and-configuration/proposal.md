## Why

El panel admin carece de configuración operativa: no hay forma de habilitar/deshabilitar métodos de pago desde la UI, y los ítems eliminados lógicamente (soft-deleted) son invisibles incluso para administradores. Este change implementa US-060 reducido: gestión de formas de pago habilitadas y visibilidad de entidades soft-deleted en los paneles existentes.

## What Changes

- **Backend — Migración Alembic**: agregar columna `activo: bool DEFAULT TRUE` a la tabla `formapago`
- **Backend — Modelo FormaPago**: agregar campo `activo: bool = True`
- **Backend — Endpoints de configuración**: `GET /admin/configuracion/formas-de-pago` y `PATCH /admin/configuracion/formas-de-pago/{codigo}` (solo ADMIN)
- **Backend — `include_deleted` param**: agregar query param `include_deleted: bool = False` a los listados de productos, categorías e ingredientes — accesible para ADMIN y STOCK, ignorado para otros roles
- **Frontend — `AdminConfiguracionPage`**: página `/admin/configuracion` con sección "Formas de pago" — cards con toggle activo/inactivo para TARJETA, RAPIPAGO, PAGO_FACIL
- **Frontend — toggle en páginas admin existentes**: agregar checkbox "Mostrar eliminados" en `AdminProductosPage`, `AdminCategoriasPage`, `AdminIngredientesPage` que envía `include_deleted=true` al backend
- **Frontend — routing y nav**: ruta `/admin/configuracion` bajo `AdminRoute` + link "Configuración" en nav para ADMIN

## Capabilities

### New Capabilities

- `admin-payment-settings`: Panel admin de formas de pago — ver todas las formas con estado activo/inactivo, togglear habilitación sin reiniciar el sistema.
- `admin-soft-delete-visibility`: Visibilidad de entidades soft-deleted en paneles admin — toggle "Mostrar eliminados" en productos, categorías e ingredientes.

### Modified Capabilities

_(ninguna — cambios puramente aditivos)_

## Impact

**Backend:**
- `backend/pagos/model.py` — agregar `activo: bool = True` a `FormaPago`
- `backend/alembic/versions/` — nueva migración: ADD COLUMN `activo` a `formapago`
- `backend/admin/schemas.py` — agregar `FormaPagoRead`, `FormaPagoUpdate`
- `backend/admin/service.py` — agregar `list_formas_pago`, `toggle_forma_pago`
- `backend/admin/router.py` — agregar 2 endpoints `/configuracion/formas-de-pago`
- `backend/productos/router.py` — agregar param `include_deleted` al listado admin
- `backend/categorias/router.py` — agregar param `include_deleted` al listado
- `backend/ingredientes/router.py` — agregar param `include_deleted` al listado

**Frontend:**
- `frontend/src/features/admin/api/adminConfiguracionApi.ts` — API client para formas de pago
- `frontend/src/features/admin/hooks/` — hooks para formas de pago
- `frontend/src/pages/admin/AdminConfiguracionPage.tsx` — página nueva
- `frontend/src/pages/admin/AdminProductosPage.tsx` — agregar toggle "Mostrar eliminados"
- `frontend/src/pages/admin/AdminCategoriasPage.tsx` — ídem
- `frontend/src/pages/admin/AdminIngredientesPage.tsx` — ídem
- `frontend/src/app/router.tsx` — ruta `/admin/configuracion`
- `frontend/src/app/routes/layout.tsx` — link "Configuración" en nav ADMIN
