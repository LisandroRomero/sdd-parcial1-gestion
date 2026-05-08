## 1. Backend — Repositorios

- [x] 1.1 Agregar `count_by_role(rol_codigo: str) -> int` a `UsuarioRepository` en `backend/usuarios/repository.py`
- [x] 1.2 Crear `UsuarioRolRepository` en `backend/usuarios/repository.py` con método `delete_all_for_user(usuario_id: int) -> None`
- [x] 1.3 Registrar `UsuarioRolRepository` en `backend/core/dependencies.py` (clave `usuario_roles`)

## 2. Backend — Schemas

- [x] 2.1 Agregar `AssignRolesRequest` a `backend/usuarios/schemas.py` con campo `roles: list[str]` (validación: no vacío, códigos válidos: ADMIN/STOCK/PEDIDOS/CLIENT)

## 3. Backend — Service

- [x] 3.1 Crear `backend/usuarios/service.py` con función `assign_roles(uow, usuario_id, body, current_user)`:
  - Buscar el usuario objetivo con `uow.repos.usuarios.get(usuario_id)` → si no existe → `NotFoundException`
  - Si `"ADMIN"` NO está en `body.roles` Y el usuario objetivo tiene ADMIN Y `uow.repos.usuarios.count_by_role("ADMIN") <= 1` → `BadRequestException(RN-RB04)`
  - `uow.repos.usuario_roles.delete_all_for_user(usuario_id)`
  - Crear nuevos `UsuarioRol` con `asignado_por_id = current_user.id` y `session.flush()`
  - Retornar usuario refrescado

## 4. Backend — Router usuarios

- [x] 4.1 Implementar `backend/usuarios/router.py` con endpoint `PUT /{id}/roles`:
  - `response_model=UserResponse`, `status_code=200`
  - Depende de `require_role("ADMIN")` y `get_uow`
  - Llama `assign_roles(...)` y `uow.commit()`

## 5. Backend — Router auth (GET /me)

- [x] 5.1 Agregar endpoint `GET /me` en `backend/auth/router.py`:
  - `response_model=UserResponse`, `status_code=200`
  - Depende solo de `get_current_user` (no necesita UoW)
  - Retorna `UserResponse.model_validate(current_user)`

## 6. Backend — Registrar router en API v1

- [x] 6.1 Importar y registrar `usuarios_router` en `backend/api/v1/router.py` con prefix `/usuarios` y tag `usuarios`

## 7. Frontend — authStore

- [x] 7.1 Actualizar tipo `User` en `frontend/src/shared/lib/stores/auth.store.ts`:
  - `roles: string[]` (reemplaza `rol: string`)
  - `nombre: string | null`, `apellido: string | null`
- [x] 7.2 Agregar método `hasRole(role: string): boolean` al store (retorna `false` si `user` es null)

## 8. Frontend — Route Guards

- [x] 8.1 Crear `frontend/src/features/auth/components/ProtectedRoute.tsx`:
  - Si `!isAuthenticated` → `<Navigate to="/login" replace />`
  - Si autenticado → `<Outlet />` (o `children`)
- [x] 8.2 Crear `frontend/src/features/auth/components/RoleGuard.tsx`:
  - Props: `role: string` (o `roles: string[]`)
  - Si `!hasRole(role)` → `<Navigate to="/403" replace />` o componente 403 inline
- [x] 8.3 Exportar `ProtectedRoute` y `RoleGuard` desde `frontend/src/features/auth/index.ts`

## 9. Verificación

- [x] 9.1 Verificar `GET /api/v1/auth/me` con token válido → 200 con roles
- [x] 9.2 Verificar `GET /api/v1/auth/me` sin token → 401
- [x] 9.3 Verificar `PUT /api/v1/usuarios/{id}/roles` como ADMIN → 200 con roles actualizados
- [x] 9.4 Verificar RN-RB04: ADMIN intenta quitarse el último rol ADMIN → 400
- [x] 9.5 Verificar `PUT /api/v1/usuarios/{id}/roles` como CLIENT → 403
