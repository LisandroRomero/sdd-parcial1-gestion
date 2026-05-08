## 1. Repositorio y Dependencias

- [x] 1.1 Crear `backend/usuarios/repository.py` con `UsuarioRepository(BaseRepository[Usuario])` que incluya `get_by_email(email: str) -> Usuario | None`
- [x] 1.2 Agregar `_register_repos()` en `backend/core/dependencies.py` que registre `UsuarioRepository` como `uow.repos.register('usuarios', UsuarioRepository)`, y llamarlo dentro de `get_uow()`

## 2. Schemas de Auth

- [x] 2.1 Crear `backend/auth/schemas.py` con `RegisterRequest` (nombre: str min 2 max 80, apellido: str min 2 max 80, email: EmailStr, password: str min 8) con `field_validator` para password
- [x] 2.2 Crear en el mismo archivo `UserResponse` (id: int, nombre: str | None, apellido: str | None, email: str, roles: list[str], created_at: datetime) con `ConfigDict(from_attributes=True)`

## 3. Servicio de Registro

- [x] 3.1 Crear `backend/auth/service.py` con función `register(uow: UnitOfWork, body: RegisterRequest) -> Usuario` que:

## 4. Router de Auth

- [x] 4.1 Crear `backend/auth/router.py` con `POST /register` que:

## 5. Wire up en API Router

- [x] 5.1 En `backend/api/v1/router.py`, descomentar la importación de `auth_router` e incluirla en `sub_routers` con prefix="/auth" y tag="auth"

## 6. Verificación

- [ ] 6.1 Arrancar el servidor con `uvicorn backend.main:app` y verificar que el endpoint aparece en Swagger UI (`/docs`)
- [ ] 6.2 Probar registro exitoso con curl/httpx contra `POST /api/v1/auth/register`
- [ ] 6.3 Probar escenarios de error: email duplicado, password corto, email inválido, campos faltantes
- [ ] 6.4 Verificar en BD que el usuario fue creado con rol CLIENT y password hasheado
