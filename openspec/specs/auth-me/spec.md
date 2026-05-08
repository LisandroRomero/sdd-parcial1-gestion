## Requirements

### Requirement: Usuario autenticado puede obtener su propio perfil

El sistema SHALL proveer un endpoint `GET /api/v1/auth/me` que retorna el perfil completo del usuario autenticado, incluyendo su lista de roles, sin exponer el `password_hash`.

#### Scenario: Perfil retornado exitosamente

- **WHEN** un usuario autenticado envía `GET /api/v1/auth/me` con un Bearer access token válido
- **THEN** el sistema retorna HTTP 200 con un `UserResponse` conteniendo `id`, `nombre`, `apellido`, `email`, `roles: list[str]` y `created_at`

#### Scenario: Token ausente

- **WHEN** un cliente envía `GET /api/v1/auth/me` sin el header `Authorization`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Token inválido o expirado

- **WHEN** un cliente envía `GET /api/v1/auth/me` con un Bearer token con firma inválida o expirado
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: El campo password_hash nunca se expone

- **WHEN** el sistema retorna el `UserResponse` de cualquier endpoint de auth
- **THEN** la respuesta no contiene el campo `password_hash` bajo ningún nombre
