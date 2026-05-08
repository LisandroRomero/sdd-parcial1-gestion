## 1. RefreshTokenRepository — nuevos métodos

- [x] 1.1 Agregar método `revoke(token_id: int) -> None` en `backend/refreshtokens/repository.py`: obtener el token por ID, asignar `revoked_at = datetime.now(timezone.utc)` y llamar `self.session.flush()`
- [x] 1.2 Agregar método `revoke_all_for_user(usuario_id: int) -> None` en `backend/refreshtokens/repository.py`: ejecutar `UPDATE refreshtoken SET revoked_at = now() WHERE usuario_id = :id AND revoked_at IS NULL` usando `update()` de SQLAlchemy con `synchronize_session="fetch"`

## 2. Schema — RefreshRequest

- [x] 2.1 Agregar clase `RefreshRequest(BaseModel)` en `backend/auth/schemas.py` con campo `refresh_token: str` y validador mínimo (non-empty)

## 3. Service — función refresh_tokens

- [x] 3.1 Crear función `refresh_tokens(uow: UnitOfWork, body: RefreshRequest) -> TokenResponse` en `backend/auth/service.py`
- [x] 3.2 Dentro de `refresh_tokens`: llamar `verify_token(body.refresh_token)` para verificar firma JWT y expiración — lanzar `UnauthorizedException` si falla
- [x] 3.3 Dentro de `refresh_tokens`: verificar que `payload.get("type") == "refresh"` — lanzar `UnauthorizedException("Token inválido")` si no coincide
- [x] 3.4 Dentro de `refresh_tokens`: calcular `token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()` y llamar `uow.repos.refresh_tokens.get_by_hash(token_hash)` — lanzar `UnauthorizedException` si retorna `None`
- [x] 3.5 Dentro de `refresh_tokens`: si `stored_token.revoked_at is not None` → detectar replay attack → llamar `uow.repos.refresh_tokens.revoke_all_for_user(stored_token.usuario_id)` → lanzar `UnauthorizedException("Sesión invalidada por seguridad. Por favor inicie sesión nuevamente.")`
- [x] 3.6 Dentro de `refresh_tokens`: extraer `usuario_id` del payload (`int(payload["sub"])`), generar nuevo access token con rol del usuario (cargar usuario desde BD via `uow.repos.usuarios.get_by_id(usuario_id)`) y nuevo refresh token
- [x] 3.7 Dentro de `refresh_tokens`: revocar el token anterior llamando `uow.repos.refresh_tokens.revoke(stored_token.id)`
- [x] 3.8 Dentro de `refresh_tokens`: persistir el nuevo hash via `uow.repos.refresh_tokens.create(usuario_id, nuevo_hash, expires_at)` y retornar `TokenResponse`

## 4. Router — endpoint POST /refresh

- [x] 4.1 Importar `refresh_tokens` del service y `RefreshRequest` del schemas en `backend/auth/router.py`
- [x] 4.2 Agregar endpoint `POST /refresh` con `response_model=TokenResponse`, `status_code=HTTP_200_OK`, decorator `@limiter.limit("10/15minutes")`, y delegar a `refresh_tokens(uow, body)` + `uow.commit()`

## 5. Verificación manual

- [x] 5.1 Iniciar el servidor y verificar que `POST /api/v1/auth/refresh` aparece en `/docs`
- [x] 5.2 Flujo completo: login → obtener refresh token → llamar /refresh → verificar nuevo par de tokens retornado y token anterior revocado en BD
- [x] 5.3 Caso replay attack: usar el mismo refresh token dos veces → primera llamada exitosa, segunda debe retornar 401 y todos los tokens del usuario deben quedar revocados en BD
- [x] 5.4 Caso token inválido: enviar string aleatorio → debe retornar 401
- [x] 5.5 Caso access token como refresh: enviar access token al endpoint → debe retornar 401
