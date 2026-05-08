## Why

Los Epics 1.1–1.4 completan el ciclo de autenticación pero el sistema no expone el perfil del usuario autenticado ni permite al ADMIN gestionar los roles de otros usuarios. Sin esto, el frontend no puede saber los roles del usuario logueado y las rutas privadas no pueden protegerse por rol.

## What Changes

- Nuevo endpoint `GET /api/v1/auth/me` → retorna el perfil completo del usuario autenticado (Bearer token requerido).
- Nuevo endpoint `PUT /api/v1/usuarios/{id}/roles` (ADMIN only) → reemplaza el conjunto de roles de un usuario. Implementa la regla RN-RB04: un ADMIN no puede quitarse su propio rol ADMIN si es el último administrador del sistema.
- Nuevo service + router en módulo `usuarios/` (actualmente vacíos).
- Frontend: actualizar tipo `User` en `authStore` para usar `roles: string[]` con los códigos reales del backend (`CLIENT`, `ADMIN`, `STOCK`, `PEDIDOS`). Agregar método `hasRole()`.
- Frontend: `ProtectedRoute` HOC — redirige al login si el usuario no está autenticado.
- Frontend: `RoleGuard` component — retorna 403 o redirige si el usuario autenticado no tiene el rol requerido.

## Capabilities

### New Capabilities

- `auth-me`: Endpoint GET /api/v1/auth/me que retorna el perfil del usuario autenticado con sus roles.
- `role-assignment`: Endpoint PUT /api/v1/usuarios/{id}/roles (ADMIN only) con seguridad RN-RB04.
- `frontend-route-guards`: ProtectedRoute HOC + RoleGuard component + authStore User type actualizado.

### Modified Capabilities

<!-- No se modifica ninguna capability existente. auth-dependencies ya define require_role y get_current_user — se usan como DI sin cambiar sus specs. -->

## Impact

- **Backend**: `backend/auth/router.py` (nuevo endpoint `/me`), `backend/usuarios/service.py` (nuevo), `backend/usuarios/router.py` (nuevo), `backend/usuarios/schemas.py` (nuevo schema `AssignRolesRequest`), `backend/api/v1/router.py` (registrar usuarios router).
- **Frontend**: `frontend/src/shared/lib/stores/auth.store.ts` (actualizar User type + hasRole), `frontend/src/features/auth/` (ProtectedRoute, RoleGuard).
- **BD**: sin migraciones — tablas `rol` y `usuariorol` ya existen con los 4 roles seed.
