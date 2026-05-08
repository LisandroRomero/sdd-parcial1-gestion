## Requirements

### Requirement: Usuario puede renovar su access token usando el refresh token

El sistema SHALL proveer un endpoint `POST /api/v1/auth/refresh` que recibe un refresh token JWT válido, verifica su existencia en BD y su estado de revocación, y retorna un nuevo par de tokens (access + refresh) revocando el anterior.

#### Scenario: Refresh exitoso con token válido

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con `{ refresh_token: "<jwt_valido>" }` y el token existe en BD con `revoked_at IS NULL` y no está expirado
- **THEN** el sistema retorna HTTP 200 con un nuevo `TokenResponse` (`access_token`, `refresh_token`, `token_type: "bearer"`, `expires_in: 1800`)

#### Scenario: Token no existe en base de datos

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con un refresh token JWT criptográficamente válido pero cuyo SHA-256 hash no existe en la tabla `refreshtoken`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Token expirado (verificación JWT)

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con un refresh token JWT con `exp` en el pasado
- **THEN** el sistema retorna HTTP 401 Unauthorized sin consultar la BD

#### Scenario: Token con firma inválida

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con un string que no es un JWT válido o fue firmado con clave diferente
- **THEN** el sistema retorna HTTP 401 Unauthorized sin consultar la BD

#### Scenario: Se pasa un access token en lugar de un refresh token

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con un access token (claim `type == "access"`) válido
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Campo refresh_token ausente

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` sin el campo `refresh_token` en el body
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con error de validación

### Requirement: El refresh token anterior se revoca al completar la rotación

El sistema SHALL revocar el refresh token presentado (`revoked_at = now()`) inmediatamente al emitir el nuevo par, garantizando que cada refresh token solo pueda ser usado una vez.

#### Scenario: Refresh token previo queda revocado tras rotación exitosa

- **WHEN** un refresh exitoso es completado
- **THEN** el registro en `refreshtoken` del token presentado tiene `revoked_at` con un timestamp no nulo

#### Scenario: Nuevo refresh token es persistido en BD

- **WHEN** un refresh exitoso es completado
- **THEN** existe un nuevo registro en `refreshtoken` con `usuario_id` del mismo usuario, `token_hash` del nuevo token, `revoked_at IS NULL`, y `expires_at = now + 7 días`

### Requirement: Detección de replay attack invalida toda la sesión del usuario

El sistema SHALL detectar el uso de un refresh token previamente revocado como indicador de compromiso de sesión, y en ese caso SHALL revocar TODOS los refresh tokens activos del usuario (token family invalidation) y retornar HTTP 401.

#### Scenario: Replay attack detectado — token ya revocado es presentado

- **WHEN** un cliente envía `POST /api/v1/auth/refresh` con un refresh token cuyo hash existe en BD con `revoked_at IS NOT NULL`
- **THEN** el sistema revoca todos los tokens activos del usuario (`UPDATE refreshtoken SET revoked_at = now() WHERE usuario_id = :id AND revoked_at IS NULL`) y retorna HTTP 401 con mensaje "Sesión invalidada por seguridad. Por favor inicie sesión nuevamente."

#### Scenario: Todos los tokens del usuario quedan revocados tras detección de replay

- **WHEN** se detecta un replay attack para el usuario con ID `X`
- **THEN** no existe ningún registro en `refreshtoken` con `usuario_id = X` y `revoked_at IS NULL`

### Requirement: Rate limiting en el endpoint de refresh

El sistema SHALL limitar las peticiones a `POST /api/v1/auth/refresh` a un máximo de 10 requests por IP en una ventana deslizante de 15 minutos.

#### Scenario: Límite no superado — request permitido

- **WHEN** una IP realiza 10 o menos requests a `POST /api/v1/auth/refresh` en 15 minutos
- **THEN** cada request es procesado normalmente

#### Scenario: Límite superado — request bloqueado

- **WHEN** una IP realiza el undécimo request a `POST /api/v1/auth/refresh` dentro de la misma ventana de 15 minutos
- **THEN** el sistema retorna HTTP 429 Too Many Requests
