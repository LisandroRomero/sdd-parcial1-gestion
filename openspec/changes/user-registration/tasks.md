## 1. Repositorio y Dependencias

- [ ] 1.1 Crear `backend/usuarios/repository.py` con `UsuarioRepository(BaseRepository[Usuario])` que incluya `get_by_email(email: str) -> Usuario | None`
- [ ] 1.2 Agregar `_register_repos()` en `backend/core/dependencies.py` que registre `UsuarioRepository` como `uow.repos.register('usuarios', UsuarioRepository)`, y llamarlo dentro de `get_uow()`

## 2. Schemas de Auth

- [ ] 2.1 Crear `backend/auth/schemas.py` con `RegisterRequest` (nombre: str min 2 max 80, apellido: str min 2 max 80, email: EmailStr, password: str min 8) con `field_validator` para password
- [ ] 2.2 Crear en el mismo archivo `UserResponse` (id: int, nombre: str | None, apellido: str | None, email: str, roles: list[str], created_at: datetime) con `ConfigDict(from_attributes=True)`

## 3. Servicio de Registro

- [ ] 3.1 Crear `backend/auth/service.py` con función `register(uow: UnitOfWork, body: RegisterRequest) -> Usuario` que:
  - Verifique unicidad de email via `uow.repos.usuarios.get_by_email()`
  - Lance HTTPException(409) si el email ya existe
  - Hashee la password con `hash_password()` de `core.security`
  - Cree el `Usuario` con nombre, apellido, email, password_hash
  - Cree el `UsuarioRol` con rol_codigo="CLIENT"
  - Retorne el usuario creado (no hace commit — el router o el UoW se encarga)

## 4. Router de Auth

- [ ] 4.1 Crear `backend/auth/router.py` con `POST /register` que:
  - Reciba `RegisterRequest` en el body
  - Reciba `UnitOfWork` vía Depends(get_uow)
  - Llame a `register(uow, body)`
  - Haga `uow.commit()`
  - Serialice respuesta con `UserResponse.model_validate(usuario)` y retorne HTTP 201
  - Si ocurre excepción, el UoW hace rollback automático

## 5. Wire up en API Router

- [ ] 5.1 En `backend/api/v1/router.py`, descomentar la importación de `auth_router` e incluirla en `sub_routers` con prefix="/auth" y tag="auth"

## 6. Verificación

- [ ] 6.1 Arrancar el servidor con `uvicorn backend.main:app` y verificar que el endpoint aparece en Swagger UI (`/docs`)
- [ ] 6.2 Probar registro exitoso con curl/httpx contra `POST /api/v1/auth/register`
- [ ] 6.3 Probar escenarios de error: email duplicado, password corto, email inválido, campos faltantes
- [ ] 6.4 Verificar en BD que el usuario fue creado con rol CLIENT y password hasheado
