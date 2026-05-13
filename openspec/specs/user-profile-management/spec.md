### Requirement: Usuario autenticado puede ver su perfil completo

El sistema SHALL proveer un endpoint `GET /api/v1/usuarios/me/perfil` que retorna el perfil completo del usuario autenticado, incluyendo `nombre`, `apellido`, `email`, `telefono`, `roles`, `activo`, `created_at`, `updated_at` y la lista de direcciones de entrega activas (`deleted_at IS NULL`). No expone `password_hash` ni refresh tokens.

#### Scenario: Perfil retornado exitosamente

- **WHEN** un usuario autenticado envía `GET /api/v1/usuarios/me/perfil` con un Bearer access token válido
- **THEN** el sistema retorna HTTP 200 con un `PerfilRead` conteniendo todos los campos del perfil y `direcciones` como lista de `DireccionEntregaRead` (solo activas)

#### Scenario: Token ausente

- **WHEN** un cliente envía `GET /api/v1/usuarios/me/perfil` sin el header `Authorization`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Token inválido o expirado

- **WHEN** un cliente envía `GET /api/v1/usuarios/me/perfil` con un Bearer token con firma inválida o expirado
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Campos sensibles nunca se exponen

- **WHEN** el sistema retorna el `PerfilRead` desde `GET /api/v1/usuarios/me/perfil`
- **THEN** la respuesta no contiene `password_hash` ni datos de refresh tokens

#### Scenario: Solo se incluyen direcciones activas

- **WHEN** un usuario tiene direcciones de entrega y algunas tienen `deleted_at` distinto de NULL
- **THEN** el campo `direcciones` de `PerfilRead` solo contiene las que tienen `deleted_at IS NULL`

### Requirement: Usuario autenticado puede editar campos básicos de su perfil

El sistema SHALL proveer un endpoint `PUT /api/v1/usuarios/me/perfil` que permite al usuario autenticado actualizar `nombre`, `apellido` y `telefono`. Los campos `email`, `password` y `roles` no son editables desde este endpoint.

#### Scenario: Actualización exitosa con campos válidos

- **WHEN** un usuario autenticado envía `PUT /api/v1/usuarios/me/perfil` con un body `PerfilUpdate` conteniendo `nombre`, `apellido` y/o `telefono` con valores válidos
- **THEN** el sistema retorna HTTP 200 con el `PerfilRead` actualizado reflejando los nuevos valores

#### Scenario: Actualización parcial — solo un campo

- **WHEN** un usuario autenticado envía `PUT /api/v1/usuarios/me/perfil` con un body que contiene solo `telefono` (los demás campos son `null`)
- **THEN** el sistema actualiza solo `telefono` y retorna HTTP 200 con el `PerfilRead` completo; los demás campos no se modifican

#### Scenario: Nombre vacío rechazado

- **WHEN** un usuario autenticado envía `PUT /api/v1/usuarios/me/perfil` con `nombre: ""`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity

#### Scenario: Apellido vacío rechazado

- **WHEN** un usuario autenticado envía `PUT /api/v1/usuarios/me/perfil` con `apellido: ""`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity

#### Scenario: Email no modificable desde este endpoint

- **WHEN** un usuario autenticado envía `PUT /api/v1/usuarios/me/perfil` con un body que intenta incluir `email`
- **THEN** el campo `email` es ignorado (o rechazado por el schema) y el email del usuario no cambia

#### Scenario: Token ausente en PUT

- **WHEN** un cliente envía `PUT /api/v1/usuarios/me/perfil` sin el header `Authorization`
- **THEN** el sistema retorna HTTP 401 Unauthorized

### Requirement: PerfilRead no expone datos administrativos internos

El sistema SHALL garantizar que el schema `PerfilRead` nunca incluya `password_hash`, tokens de sesión, ni campos de auditoría interna como `deleted_at`.

#### Scenario: PerfilRead no contiene password_hash

- **WHEN** el sistema serializa un `PerfilRead` para cualquier usuario
- **THEN** el JSON resultante no contiene la clave `password_hash`

#### Scenario: PerfilRead no contiene deleted_at del usuario

- **WHEN** el sistema serializa un `PerfilRead`
- **THEN** el JSON resultante no contiene la clave `deleted_at`
