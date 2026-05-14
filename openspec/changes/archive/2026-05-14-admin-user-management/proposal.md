## Why

El sistema no tiene panel de administración de usuarios. El módulo `backend/admin/` existe pero está vacío, el router no está registrado, y el frontend no tiene páginas admin. Además, el login no valida el campo `activo` del usuario, por lo que usuarios desactivados pueden seguir autenticándose. Este change implementa US-053..US-055: listar, editar y desactivar usuarios desde el panel admin.

## What Changes

- **Backend — `backend/admin/`**: implementar módulo completo con schemas, repository, service y router para gestión de usuarios
  - `GET /api/v1/admin/usuarios` — listado paginado con búsqueda (nombre/email) y filtro por rol (solo ADMIN)
  - `PUT /api/v1/admin/usuarios/{id}` — edición de datos y rol (respeta RN-RB04: último ADMIN no se puede degradar)
  - `PATCH /api/v1/admin/usuarios/{id}/estado` — activar/desactivar usuario + invalidación de refresh tokens
- **Backend — `backend/api/v1/router.py`**: registrar router de admin con prefix `/admin`
- **Backend — `backend/auth/service.py`**: agregar validación `activo=False` → `ForbiddenException("Cuenta desactivada")` en el flujo de login (US-055)
- **Frontend — páginas admin**: crear `AdminUsuariosPage` con tabla de usuarios, búsqueda, filtro por rol y paginación
- **Frontend — features/admin**: hooks (useListarUsuariosAdmin, useToggleEstadoUsuario, useActualizarUsuarioAdmin) + llamadas a la API
- **Frontend — routing**: agregar ruta `/admin/usuarios` protegida por rol ADMIN

## Capabilities

### New Capabilities

- `admin-user-panel`: Panel de administración de usuarios — listado paginado con búsqueda y filtro, edición de datos/rol, activar/desactivar con invalidación de tokens. Acceso exclusivo para rol ADMIN.

### Modified Capabilities

- `user-login`: Agregar validación de cuenta activa — si `activo=False`, el login retorna 403 con mensaje "Cuenta desactivada" antes de emitir tokens.

## Impact

**Backend:**
- `backend/admin/schemas.py` — UsuarioAdminRead, UsuarioAdminUpdate, EstadoUsuarioUpdate, UsuarioAdminListRead
- `backend/admin/repository.py` — list_usuarios (search ilike, filter por rol), get_by_id
- `backend/admin/service.py` — list_usuarios, update_usuario (con RN-RB04 + token invalidation), toggle_estado
- `backend/admin/router.py` — 3 endpoints protegidos con ADMIN guard
- `backend/api/v1/router.py` — incluir admin_router con prefix `/admin`
- `backend/auth/service.py` — check activo en función `login()`

**Frontend:**
- `frontend/src/pages/admin/AdminUsuariosPage.tsx` — página principal del panel
- `frontend/src/features/admin/` — hooks y API client para usuarios admin
- `frontend/src/entities/admin/types.ts` — tipos AdminUsuarioRead, AdminUsuarioUpdate
- `frontend/src/app/routes/index.tsx` — ruta `/admin/usuarios` con guard ADMIN
