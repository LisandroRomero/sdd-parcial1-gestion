## 1. Schemas

- [x] 1.1 Agregar `PerfilRead` en `backend/usuarios/schemas.py` con campos: `id`, `nombre`, `apellido`, `email`, `telefono`, `roles: list[str]`, `activo`, `created_at`, `updated_at` y `direcciones: list[DireccionEntregaRead]`
- [x] 1.2 Agregar `PerfilUpdate` en `backend/usuarios/schemas.py` con campos opcionales: `nombre: Optional[str]`, `apellido: Optional[str]`, `telefono: Optional[str]`; con `field_validator` que rechace strings vacíos (`""`) para `nombre` y `apellido` con 422
- [x] 1.3 Agregar el import de `DireccionEntregaRead` desde `backend.direcciones.schemas` en `backend/usuarios/schemas.py`

## 2. Service

- [x] 2.1 Agregar función `get_perfil(uow: UnitOfWork, usuario_id: int) -> PerfilRead` en `backend/usuarios/service.py` que: recarga el usuario con sus relaciones (`roles`, `direcciones`) desde el UoW y retorna `PerfilRead` con direcciones activas (`deleted_at IS NULL`)
- [x] 2.2 Agregar función `update_perfil(uow: UnitOfWork, usuario_id: int, data: PerfilUpdate) -> PerfilRead` en `backend/usuarios/service.py` que: carga el usuario desde el UoW, aplica los campos no-`None` de `data`, persiste y retorna `PerfilRead` actualizado
- [x] 2.3 Asegurarse de que `update_perfil` no modifique `email`, `password_hash` ni `roles` bajo ninguna circunstancia

## 3. Router

- [x] 3.1 Agregar endpoint `GET /me/perfil` en `backend/usuarios/router.py` con `response_model=PerfilRead`, dependencias `get_current_user` y `get_uow`, que llama a `get_perfil(uow, current_user.id)`
- [x] 3.2 Agregar endpoint `PUT /me/perfil` en `backend/usuarios/router.py` con `response_model=PerfilRead`, dependencias `get_current_user` y `get_uow`, que llama a `update_perfil(uow, current_user.id, body)` y hace `uow.commit()`
- [x] 3.3 Verificar que los imports en `router.py` incluyan los nuevos schemas `PerfilRead`, `PerfilUpdate` y las funciones `get_perfil`, `update_perfil`

## 4. Verificación

- [x] 4.1 Verificar manualmente con `curl` o Swagger UI que `GET /api/v1/usuarios/me/perfil` retorna 200 con el perfil completo incluyendo `direcciones`
- [x] 4.2 Verificar que `PUT /api/v1/usuarios/me/perfil` con `{"nombre": ""}` retorna 422
- [x] 4.3 Verificar que `PUT /api/v1/usuarios/me/perfil` con solo `{"telefono": "1234567890"}` actualiza solo el teléfono sin tocar `nombre` ni `apellido`
- [x] 4.4 Verificar que la respuesta de ambos endpoints no contiene `password_hash` ni `deleted_at`
- [x] 4.5 Verificar que `GET /api/v1/auth/me` sigue funcionando sin cambios (no regresión)
