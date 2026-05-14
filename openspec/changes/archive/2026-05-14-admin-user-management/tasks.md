## 1. Backend — Auth: check de cuenta activa en login

- [x] 1.1 En `backend/auth/service.py`, función `login()`: agregar check después de la validación de password — si `usuario.activo is False` → raise `ForbiddenException(detail="Cuenta desactivada")`

## 2. Backend — Admin schemas

- [x] 2.1 Escribir `backend/admin/schemas.py` completo con:
  - `UsuarioAdminRead(id, nombre, apellido, email, activo, roles: list[str], created_at)` con `from_attributes=True`
  - `UsuarioAdminUpdate(nombre?, apellido?, email?, roles?: list[str])` todos opcionales
  - `EstadoUsuarioUpdate(activo: bool)`
  - `UsuarioAdminListRead(items: list[UsuarioAdminRead], total, page, size, pages)`

## 3. Backend — Admin repository

- [x] 3.1 Escribir `backend/admin/repository.py` con clase `AdminRepository(BaseRepository[Usuario])`:
  - `list_usuarios(buscar?, rol?, limit, offset)` → `tuple[list[Usuario], int]`
    - Búsqueda: `ilike` sobre `nombre OR apellido OR email` cuando `buscar` provisto
    - Filtro por rol: JOIN a `UsuarioRol` cuando `rol` provisto
    - Retorna `(items, total_count)` con dos queries separadas
  - `get_by_id(id) -> Optional[Usuario]` — alias de `session.get(Usuario, id)`

## 4. Backend — Admin service

- [x] 4.1 Escribir `backend/admin/service.py` con tres funciones:
  - `list_usuarios(uow, buscar?, rol?, page, size)` → `UsuarioAdminListRead`
    - Delega al admin repository y arma la respuesta paginada
  - `update_usuario(uow, usuario_id, body: UsuarioAdminUpdate)` → `UsuarioAdminRead`
    - Buscar usuario (404 si no existe)
    - Si `body.roles` no es None: verificar RN-RB04 (`count_by_role("ADMIN")` si se quita ADMIN), actualizar roles via `usuario_roles` repo, revocar refresh tokens con `uow.repos.refresh_tokens.revoke_all_for_user(usuario_id)`
    - Si `body.nombre/apellido/email`: actualizar campos directamente en el modelo
  - `toggle_estado(uow, usuario_id, body: EstadoUsuarioUpdate)` → `UsuarioAdminRead`
    - Buscar usuario (404 si no existe)
    - Actualizar `usuario.activo = body.activo`
    - Si `body.activo is False`: revocar refresh tokens con `revoke_all_for_user`

## 5. Backend — Admin router

- [x] 5.1 Escribir `backend/admin/router.py` con 3 endpoints, todos protegidos por `Depends(require_role("ADMIN"))`:
  - `GET /usuarios` → `response_model=UsuarioAdminListRead` — llama `list_usuarios` con params `buscar`, `rol`, `page`, `size`
  - `PUT /usuarios/{usuario_id}` → `response_model=UsuarioAdminRead` — llama `update_usuario`
  - `PATCH /usuarios/{usuario_id}/estado` → `response_model=UsuarioAdminRead` — llama `toggle_estado`

## 6. Backend — Registrar router

- [x] 6.1 En `backend/api/v1/router.py`: importar `router as admin_router` de `backend.admin.router` y agregarlo a `sub_routers` con prefix `/admin` y tag `"admin"`

## 7. Frontend — Types

- [x] 7.1 Crear `frontend/src/entities/admin/types.ts` con interfaces:
  - `AdminUsuarioRead` (id, nombre, apellido, email, activo, roles: string[], created_at)
  - `AdminUsuarioUpdate` (nombre?, apellido?, email?, roles?: string[])
  - `EstadoUsuarioUpdate` (activo: boolean)
  - `AdminUsuarioListRead` (items, total, page, size, pages)
  - `AdminUsuariosParams` (buscar?, rol?, page?, size?)

## 8. Frontend — API client

- [x] 8.1 Crear `frontend/src/features/admin/api/adminUsuariosApi.ts` con funciones usando la instancia de axios existente:
  - `listarUsuariosAdmin(params: AdminUsuariosParams)` → `Promise<AdminUsuarioListRead>`
  - `actualizarUsuarioAdmin(id: number, body: AdminUsuarioUpdate)` → `Promise<AdminUsuarioRead>`
  - `toggleEstadoUsuario(id: number, body: EstadoUsuarioUpdate)` → `Promise<AdminUsuarioRead>`

## 9. Frontend — Hooks TanStack Query

- [x] 9.1 Crear `frontend/src/features/admin/hooks/useListarUsuariosAdmin.ts` — `useQuery` sobre `listarUsuariosAdmin` con queryKey `['admin', 'usuarios', params]`
- [x] 9.2 Crear `frontend/src/features/admin/hooks/useToggleEstadoUsuario.ts` — `useMutation` sobre `toggleEstadoUsuario` con `invalidateQueries` al completar
- [x] 9.3 Crear `frontend/src/features/admin/hooks/useActualizarUsuarioAdmin.ts` — `useMutation` sobre `actualizarUsuarioAdmin` con `invalidateQueries` al completar

## 10. Frontend — Página AdminUsuariosPage

- [x] 10.1 Crear `frontend/src/pages/admin/AdminUsuariosPage.tsx` con:
  - Tabla con columnas: nombre+apellido, email, roles (badges), estado (badge activo/inactivo), fecha de registro, acciones
  - Input de búsqueda con debounce 400ms
  - Select de filtro por rol (CLIENT, ADMIN, GESTOR_PEDIDOS, GESTOR_STOCK)
  - Paginación usando el componente existente `OrderPagination` o uno equivalente
  - Toggle de estado inline (botón en columna Acciones que llama `useToggleEstadoUsuario`)
  - Modal de edición de datos y rol (campos: nombre, apellido, email, roles — multiselect)

## 11. Frontend — Routing

- [x] 11.1 En `frontend/src/app/router.tsx`: agregar ruta lazy `/admin/usuarios` con `React.lazy(() => import('@/pages/admin/AdminUsuariosPage'))` protegida por guard ADMIN (`AdminRoute` creado en `frontend/src/features/auth/components/AdminRoute.tsx` y exportado desde el index de features/auth)
