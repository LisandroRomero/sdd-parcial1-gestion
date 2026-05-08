## 1. Rate Limiting Setup (slowapi)

- [x] 1.1 Crear `backend/core/rate_limit.py` con el `Limiter` global usando `key_func=get_remote_address`
- [x] 1.2 Registrar el `Limiter` en `main.py`: `app.state.limiter = limiter` y agregar el handler de `RateLimitExceeded` que retorna HTTP 429

## 2. RefreshToken Repository

- [x] 2.1 Implementar `RefreshTokenRepository` en `backend/refreshtokens/repository.py` heredando `BaseRepository[RefreshToken]` con método `create(usuario_id, token_hash, expires_at)` y método `get_by_hash(token_hash)`

## 3. Register Repository in UoW

- [x] 3.1 Registrar `RefreshTokenRepository` en `_register_repos()` de `backend/core/dependencies.py` con la key `"refresh_tokens"`

## 4. Schemas

- [x] 4.1 Agregar `LoginRequest` a `backend/auth/schemas.py` con campos `email: EmailStr` y `password: str` (validación: password mínimo 8 caracteres)
- [x] 4.2 Agregar `TokenResponse` a `backend/auth/schemas.py` con campos `access_token: str`, `refresh_token: str`, `token_type: str = "bearer"`, `expires_in: int`

## 5. Login Service

- [x] 5.1 Implementar función `login(uow: UnitOfWork, body: LoginRequest) -> TokenResponse` en `backend/auth/service.py`:
  - buscar usuario por email con `uow.repos.usuarios.get_by_email()`
  - verificar password con `verify_password()` — lanzar `UnauthorizedException("Credenciales inválidas")` si email no existe o password no coincide
  - obtener rol primario del usuario (primer elemento de `usuario.roles`)
  - generar access token con `create_access_token(subject=str(usuario.id), data={"role": rol})`
  - generar refresh token con `create_refresh_token(subject=str(usuario.id))`
  - calcular SHA-256 del refresh token: `hashlib.sha256(refresh_token.encode()).hexdigest()`
  - persistir con `uow.repos.refresh_tokens.create(usuario_id=usuario.id, token_hash=token_hash, expires_at=now + 7 días)`
  - retornar `TokenResponse` con `expires_in = settings.access_token_expire_minutes * 60`

## 6. Login Endpoint

- [x] 6.1 Agregar endpoint `POST /login` en `backend/auth/router.py` con `@limiter.limit("5/15minutes")`, `response_model=TokenResponse`, `status_code=HTTP_200_OK`; delegar a `login(uow, body)` y llamar `uow.commit()` antes de retornar

## 7. Verification

- [x] 7.1 Verificar que `POST /api/v1/auth/login` con credenciales válidas retorna HTTP 200 con `access_token`, `refresh_token`, `token_type="bearer"`, `expires_in=1800`
- [x] 7.2 Verificar que con email inexistente o password incorrecto retorna HTTP 401 con mensaje "Credenciales inválidas"
- [x] 7.3 Verificar que con campos faltantes o email inválido retorna HTTP 422
- [x] 7.4 Verificar que el refresh token se guarda en la tabla `refreshtoken` con `token_hash` de 64 chars hex y `revoked_at = NULL`
- [x] 7.5 Verificar que el payload del access token decodificado contiene el claim `role`
