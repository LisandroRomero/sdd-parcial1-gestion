## Why

El access token tiene TTL de 30 minutos. Sin un endpoint de refresh, el usuario debe re-loguearse manualmente cada 30 minutos, lo que destruye la experiencia de uso. Este change agrega `POST /api/v1/auth/refresh` para que el frontend pueda renovar el access token silenciosamente usando el refresh token de 7 días almacenado en BD.

## What Changes

- **Nuevo endpoint** `POST /api/v1/auth/refresh`: recibe un refresh token en el body, lo valida contra BD, rota el par de tokens y retorna un nuevo `TokenResponse`.
- **Detección de replay attack**: si el refresh token recibido ya fue revocado (`revoked_at IS NOT NULL`), se activa la invalidación de toda la familia de tokens del usuario (todos los refresh tokens activos quedan revocados).
- **Nuevos métodos en `RefreshTokenRepository`**: `revoke(token_id)` y `revoke_all_for_user(usuario_id)` para soportar la rotación y la detección de replay.
- **Nuevo schema** `RefreshRequest`: body del endpoint con campo `refresh_token: str`.
- **Rate limiting**: 10 requests / 15 minutos por IP en el endpoint de refresh.

## Capabilities

### New Capabilities

- `token-refresh`: Rotación de refresh tokens con detección de replay attack — el endpoint valida el token en BD, rota el par y detecta uso de tokens ya revocados (token family invalidation).

### Modified Capabilities

- `user-login`: El spec existente ya cubre la persistencia del refresh token en BD. No hay cambio de requisitos — se extiende el comportamiento downstream con el nuevo endpoint.

## Impact

- **Backend**: `backend/auth/service.py` (nueva función `refresh_tokens`), `backend/auth/router.py` (nuevo endpoint), `backend/auth/schemas.py` (nuevo `RefreshRequest`), `backend/refreshtokens/repository.py` (métodos `revoke` y `revoke_all_for_user`).
- **BD**: Sin cambios de esquema — `RefreshToken` ya tiene `revoked_at` nullable desde la migración del change `database-schema-and-seed`.
- **Dependencias**: `slowapi` ya configurado — solo se agrega el decorator con nuevo límite.
- **Frontend** (fuera de scope de este change): el interceptor Axios que llama a este endpoint se implementa en Epic 1.6 (`frontend-auth-interceptors`).
