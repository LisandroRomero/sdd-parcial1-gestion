## Why

Los usuarios que hacen login obtienen un par de tokens (access + refresh). Sin un endpoint de logout, el refresh token persiste activo en base de datos indefinidamente — el usuario no puede invalidar su sesión de forma explícita, lo que es un riesgo de seguridad ante robo de dispositivo o token comprometido.

## What Changes

- Nuevo endpoint `POST /api/v1/auth/logout` que recibe el `refresh_token` en el body y lo revoca en BD (`revoked_at = now()`).
- El endpoint requiere autenticación (Bearer access token válido).
- Responde `204 No Content` tras revocar exitosamente.
- Si el `refresh_token` no existe en BD o ya está revocado, responde `400 Bad Request`.
- Si el access token no es válido, responde `401 Unauthorized`.

## Capabilities

### New Capabilities

- `auth-logout`: Endpoint de cierre de sesión que invalida el refresh token activo del usuario en BD.

### Modified Capabilities

<!-- No se modifican capabilities existentes. La mecánica de revocación ya existe en token-refresh;
     logout solo introduce un endpoint nuevo que la invoca. -->

## Impact

- **Backend**: nuevo método en `RefreshTokenRepository` (`revoke_by_token`), nuevo método en `AuthService` (`logout`), nuevo endpoint en `auth/router.py`.
- **Módulos afectados**: `backend/refreshtokens/`, `backend/auth/`.
- **BD**: usa la columna `revoked_at` ya existente en la tabla `refreshtoken` — sin migraciones nuevas.
- **Dependencias**: requiere `get_current_user` (DI de auth ya implementada en 1.2).
