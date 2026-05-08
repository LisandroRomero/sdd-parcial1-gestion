## ADDED Requirements

### Requirement: Usuario autenticado puede cerrar sesión explícitamente

El sistema SHALL proveer un endpoint `POST /api/v1/auth/logout` que recibe el `refresh_token` del usuario en el body, verifica que exista en BD, que no esté revocado, y que pertenezca al usuario autenticado (Bearer access token), y lo revoca estableciendo `revoked_at = now()`.

#### Scenario: Logout exitoso

- **WHEN** un usuario autenticado envía `POST /api/v1/auth/logout` con un Bearer access token válido y un `refresh_token` que existe en BD con `revoked_at IS NULL` y pertenece a ese usuario
- **THEN** el sistema establece `revoked_at = now()` en el registro del token y retorna HTTP 204 No Content sin body

#### Scenario: Access token ausente

- **WHEN** un cliente envía `POST /api/v1/auth/logout` sin el header `Authorization`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Access token inválido o expirado

- **WHEN** un cliente envía `POST /api/v1/auth/logout` con un Bearer token con firma inválida o expirado
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Refresh token no existe en BD

- **WHEN** un usuario autenticado envía `POST /api/v1/auth/logout` con un `refresh_token` cuyo SHA-256 hash no existe en la tabla `refreshtoken`
- **THEN** el sistema retorna HTTP 400 Bad Request

#### Scenario: Refresh token ya fue revocado

- **WHEN** un usuario autenticado envía `POST /api/v1/auth/logout` con un `refresh_token` cuyo hash existe en BD con `revoked_at IS NOT NULL`
- **THEN** el sistema retorna HTTP 400 Bad Request

#### Scenario: Refresh token pertenece a otro usuario

- **WHEN** un usuario autenticado envía `POST /api/v1/auth/logout` con un `refresh_token` cuyo hash existe en BD pero el `usuario_id` del registro no coincide con el `id` del usuario autenticado
- **THEN** el sistema retorna HTTP 400 Bad Request

#### Scenario: Campo refresh_token ausente en el body

- **WHEN** un cliente envía `POST /api/v1/auth/logout` sin el campo `refresh_token` en el body
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con error de validación
