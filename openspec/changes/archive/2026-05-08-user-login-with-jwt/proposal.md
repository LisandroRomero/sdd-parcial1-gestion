## Why

El registro de usuarios (Epic 1.1) ya está implementado y verificado. Los usuarios pueden crear cuentas pero no tienen forma de autenticarse para acceder al sistema. Este change implementa el endpoint de login que emite un JWT access token (30 min) y un refresh token (7 días), habilitando el acceso autenticado a todos los endpoints protegidos de la API.

## What Changes

- **Nuevo endpoint** `POST /api/v1/auth/login`: autentica con email + password, retorna `TokenResponse` con access token + refresh token.
- **Nuevos schemas** `LoginRequest` y `TokenResponse` agregados a `backend/auth/schemas.py`.
- **Nueva función `login()`** en `backend/auth/service.py`: verifica credenciales, genera tokens, persiste refresh token en BD.
- **Nuevo `RefreshTokenRepository`** en `backend/refreshtokens/repository.py`: operaciones CRUD de refresh tokens.
- **Rate limiting** en el endpoint `/auth/login` via `slowapi`: máximo 5 intentos por IP en una ventana de 15 minutos.
- **Registro del repositorio** `RefreshTokenRepository` en `backend/core/dependencies.py` via `_register_repos()`.
- **Almacenamiento seguro del refresh token**: se guarda el SHA-256 hash en la columna `token_hash` de la tabla `refreshtoken` (nunca el token en texto plano).
- **Wire-up**: el router de auth expone el nuevo endpoint en el mismo `APIRouter` que ya maneja `/register`.

## Capabilities

### New Capabilities

- `user-login`: Autenticación de usuarios registrados — verifica credenciales, genera access token JWT + refresh token, persiste refresh token hasheado en BD, aplica rate limiting por IP.

### Modified Capabilities

- `jwt-auth`: Se agrega el requisito de que `create_access_token` incluye el claim `role` del usuario en el payload del JWT para que los endpoints protegidos puedan leer el rol sin consultar BD en cada request.

## Impact

- **`backend/auth/router.py`**: nuevo endpoint `POST /login` con rate limiting.
- **`backend/auth/schemas.py`**: nuevos schemas `LoginRequest`, `TokenResponse`.
- **`backend/auth/service.py`**: nueva función `login()`.
- **`backend/refreshtokens/repository.py`**: implementar `RefreshTokenRepository` (actualmente vacío).
- **`backend/core/dependencies.py`**: registrar `RefreshTokenRepository` en `_register_repos()`.
- **`backend/core/config.py`** (lectura): `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `REFRESH_TOKEN_EXPIRE_DAYS=7` ya están configurados.
- **`backend/core/security.py`** (lectura): `create_access_token`, `create_refresh_token`, `verify_password` ya están implementados.
- **`slowapi`**: debe estar en `requirements.txt` y configurado en el app (`Limiter` + `add_exception_handler`).
- **Dependencia**: Epic 1.1 (`user-registration`) ✅ — necesita usuarios existentes en BD.
