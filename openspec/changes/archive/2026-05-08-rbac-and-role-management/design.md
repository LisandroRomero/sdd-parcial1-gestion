## Context

El backend tiene `get_current_user` y `require_role` operativos desde 0.4. Los modelos `Rol`, `UsuarioRol` y `Usuario` existen con las relaciones correctas. La tabla `rol` tiene los 4 registros seed (ADMIN, STOCK, PEDIDOS, CLIENT). El módulo `usuarios/` tiene model, schemas y repository, pero su `router.py` está vacío y no existe `service.py`.

El frontend tiene `authStore` con un tipo `User` incorrecto (`rol: string` singular, código en snake_case minúscula) que no coincide con los códigos reales del backend (`CLIENT`, `ADMIN`, `STOCK`, `PEDIDOS`) ni con el modelo M2M (`roles: list[str]`).

## Goals / Non-Goals

**Goals:**
- Exponer `GET /api/v1/auth/me` para que el frontend obtenga el perfil completo del usuario autenticado.
- Implementar `PUT /api/v1/usuarios/{id}/roles` (ADMIN only) con semántica REPLACE y regla RN-RB04.
- Inicializar `usuarios/service.py` y `usuarios/router.py`, y registrar el router en `api/v1/router.py`.
- Corregir el tipo `User` en `authStore` y agregar `hasRole()`.
- Crear `ProtectedRoute` y `RoleGuard` en `features/auth/`.

**Non-Goals:**
- CRUD completo de usuarios (7.2).
- Soft delete de usuarios (7.2).
- Axios interceptors / refresh automático en FE (1.6).
- `require_role` DI — ya implementado, no se modifica.

## Decisions

### 1. PUT /usuarios/{id}/roles usa semántica REPLACE

El cliente envía la lista completa de roles deseados (`{ roles: ["ADMIN", "CLIENT"] }`). El service borra todos los `UsuarioRol` existentes del usuario y recrea los nuevos en una transacción. Alternativa descartada: POST/DELETE separados por rol. El REPLACE es más simple y atómico — evita estados intermedios inconsistentes.

### 2. RN-RB04: verificar último ADMIN ANTES del reemplazo

Si `ADMIN` no está en la nueva lista de roles Y el usuario actualmente tiene el rol ADMIN, verificar que existan otros usuarios con `rol_codigo = "ADMIN"` y `revoked_at` irrelevante (simplemente contar `UsuarioRol` con `rol_codigo = "ADMIN"` excluyendo este usuario). Si el conteo es 0 → `BadRequestException("No puede quitarse el rol ADMIN: es el último administrador del sistema")`.

### 3. GET /auth/me usa get_current_user DI existente

El endpoint simplemente retorna `UserResponse.model_validate(current_user)`. No necesita UoW — solo la sesión que ya tiene `get_current_user`. Así se evita abrir una segunda sesión innecesaria.

### 4. Frontend: roles como string[] con códigos exactos del backend

El tipo `User.roles` pasa a `string[]` con valores `"CLIENT"`, `"ADMIN"`, `"STOCK"`, `"PEDIDOS"` — los mismos que devuelve `UserResponse.roles`. `hasRole(role: string)` hace `this.user?.roles.includes(role) ?? false`. Sin mapeo de nombres: usar los códigos directamente evita bugs de sincronización.

### 5. ProtectedRoute y RoleGuard como wrappers de React Router

`ProtectedRoute`: si `!isAuthenticated` → `<Navigate to="/login" replace />`. `RoleGuard`: si `isAuthenticated && !hasRole(role)` → `<Navigate to="/403" replace />` (o componente 403 inline). Ambos usan `useAuthStore` directo — sin props de usuario para evitar prop-drilling.

### 6. Nuevo UsuarioRolRepository para el service

El service de role-assignment necesita borrar y recrear `UsuarioRol`. Se agrega un `UsuarioRolRepository` en `backend/usuarios/repository.py` con `delete_all_for_user(usuario_id)` y el repository existente ya tiene `get_by_email`. El `UsuarioRepository` necesita un método `count_by_role(rol_codigo)` para el chequeo RN-RB04.

## Risks / Trade-offs

- **REPLACE atómico borra y recrea**: si la lista nueva está vacía, el usuario queda sin roles — queda como usuario sin permisos. Mitigación: validar en el schema que `roles` no puede estar vacío; siempre debe tener al menos un rol.
- **authStore type change es breaking**: cualquier código FE que use `user.rol` falla en compilación. Mitigación: TypeScript lo detecta en build — no hay riesgo en runtime.

## Migration Plan

1. Backend: agregar `UsuarioRolRepository` + `count_by_role` en `usuarios/repository.py`.
2. Backend: crear `usuarios/service.py` con `assign_roles` + `get_me`.
3. Backend: implementar `usuarios/router.py` con `PUT /{id}/roles`.
4. Backend: agregar `GET /me` en `auth/router.py`.
5. Backend: registrar `usuarios_router` en `api/v1/router.py`.
6. Frontend: actualizar `User` type + `hasRole()` en `auth.store.ts`.
7. Frontend: crear `ProtectedRoute` y `RoleGuard` en `features/auth/`.
