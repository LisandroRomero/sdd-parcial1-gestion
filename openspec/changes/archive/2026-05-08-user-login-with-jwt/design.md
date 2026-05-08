## Context

El endpoint de registro (POST /api/v1/auth/register) ya está implementado y verificado (Epic 1.1). La infraestructura base de auth está completa: `bcrypt` directo para hashing, `python-jose`/`PyJWT` para JWT, `create_access_token` / `create_refresh_token` / `verify_password` en `backend/core/security.py`, `get_current_user` y `require_role` en `backend/core/dependencies.py`.

El modelo `RefreshToken` en BD almacena `token_hash` (SHA-256, CHAR(64)), `expires_at`, `revoked_at`, y FK a `usuario`. El `RefreshTokenRepository` existe como archivo pero está vacío — necesita implementación.

`slowapi>=0.1.9` ya está en `requirements.txt`. El `Limiter` aún no está integrado en `main.py` — se debe agregar junto con el handler de `RateLimitExceeded`.

## Goals / Non-Goals

**Goals:**

- Implementar `POST /api/v1/auth/login` que autentica email+password y retorna access token + refresh token.
- Persistir el refresh token en BD (columna `token_hash` = SHA-256 del JWT string) para soporte de invalidación server-side.
- Aplicar rate limiting de 5 intentos / 15 minutos por IP sobre el endpoint de login.
- Retornar `TokenResponse` con `access_token`, `refresh_token`, `token_type="bearer"`, `expires_in` (en segundos).
- Incluir el claim `role` del usuario en el payload del access token para que los guards downstream puedan leer el rol sin hit a BD.

**Non-Goals:**

- Token rotation (POST /auth/refresh) → Epic 1.3.
- Logout (POST /auth/logout) → Epic 1.4.
- RBAC completo y guards de rol → Epic 1.5.
- Frontend login form → pendiente.

## Decisions

### 1. Refresh token almacenado como SHA-256 hash en BD

El token JWT completo se genera con `create_refresh_token()` y se retorna al cliente. En BD solo se guarda `hashlib.sha256(token.encode()).hexdigest()` en `token_hash`. Esto sigue el mismo principio que almacenar contraseñas: si la BD es comprometida, los tokens no son utilizables directamente.

**Alternativa descartada**: Almacenar token completo. Viola principio de mínimo privilegio y es innecesario — el token firmado es la fuente de verdad para verificación de firma; la BD solo necesita saber si está revocado.

### 2. Rate limiting con slowapi en el app-level Limiter

Se crea un `Limiter` global en `backend/core/rate_limit.py` con `key_func=get_remote_address`. Se registra en `main.py` como `app.state.limiter` y se agrega el handler de `RateLimitExceeded`. El endpoint de login usa el decorator `@limiter.limit("5/15minutes")`.

**Alternativa descartada**: Middleware propio de rate limiting. Más complejidad sin beneficio — slowapi tiene integración nativa con FastAPI y Starlette.

### 3. login() service no usa servicio de usuarios intermedio

`AuthService.login()` (función libre en `service.py`) recibe el `UoW`, consulta directamente `uow.repos.usuarios.get_by_email()` y `uow.repos.refresh_tokens.create()`. No existe un `UsuarioService` intermedio — consistente con la decisión tomada en el change de registro.

### 4. RefreshTokenRepository registrado en dependencies.py

`_register_repos()` en `backend/core/dependencies.py` se extiende para registrar `RefreshTokenRepository` con la key `"refresh_tokens"`. El service accede via `uow.repos.refresh_tokens`.

### 5. claim `role` en el access token

`create_access_token` ya acepta el parámetro `data: dict | None`. Al generar el token de login, se pasa `data={"role": rol_primario}` donde `rol_primario` es el primer rol del usuario (CLIENT en el caso estándar). Esto permite que `get_current_user` o guards futuros lean el rol del payload sin consultar BD.

**Trade-off**: El role en el token puede quedar stale si se cambia el rol del usuario. Para el alcance del parcial esto es aceptable — la gestión de roles es Epic 1.5 y puede invalidar tokens activos vía logout.

### 6. Respuesta 401 unificada para credenciales inválidas

Si el email no existe o el password no coincide, el service lanza `UnauthorizedException` con el mismo mensaje genérico ("Credenciales inválidas"). Nunca se distingue "email no existe" de "password incorrecto" para evitar user enumeration.

## Risks / Trade-offs

- **[Risk] slowapi no está integrado en main.py** → El decorator `@limiter.limit()` lanza error si `app.state.limiter` no está configurado. Mitigación: la tarea de setup del Limiter debe ir ANTES de la tarea del endpoint.
- **[Risk] RefreshToken expires_at timezone** → El modelo usa `DateTime(timezone=True)`. Al crear el registro, `expires_at` debe ser `datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)`. Mitigación: siempre usar `datetime.now(timezone.utc)` (nunca `datetime.utcnow()` que es naive).
- **[Trade-off] Role claim stale** → Si el usuario tiene múltiples roles, solo se incluye uno en el token. La lógica completa de RBAC se implementa en Epic 1.5.

## Migration Plan

No hay cambios de esquema de BD — `RefreshToken` ya existe y fue creada en la migración Alembic del change `database-schema-and-seed`. Solo se agrega código de aplicación y se configura slowapi.

Pasos de deploy:
1. Agregar Limiter a `main.py`.
2. Implementar `RefreshTokenRepository`.
3. Registrar repo en `dependencies.py`.
4. Agregar schemas `LoginRequest` / `TokenResponse`.
5. Implementar `login()` en `service.py`.
6. Agregar endpoint en `router.py`.

Rollback: revertir los archivos Python modificados. No hay cambio de BD.

## Open Questions

- ¿El `expires_in` del `TokenResponse` debe ser en segundos del access token? → Sí, según spec: `expires_in: int` en segundos (= `ACCESS_TOKEN_EXPIRE_MINUTES * 60 = 1800`).
- ¿El limiter debe contar solo intentos fallidos o todos los requests al endpoint? → Todos los requests (comportamiento estándar de slowapi). Simplifica la implementación y es suficiente para el parcial.
