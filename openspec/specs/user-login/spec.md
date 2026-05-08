## Requirements

### Requirement: Usuario puede iniciar sesión con email y password

El sistema SHALL autenticar a un usuario registrado que provea email y password válidos, retornando un access token JWT (30 min) y un refresh token (7 días).

#### Scenario: Login exitoso

- **WHEN** un usuario envía `POST /api/v1/auth/login` con `{ email: "juan@example.com", password: "securepass123" }` y las credenciales coinciden con un usuario activo en BD
- **THEN** el sistema retorna HTTP 200 con `{ access_token, refresh_token, token_type: "bearer", expires_in: 1800 }`

#### Scenario: Email no registrado

- **WHEN** un usuario envía `POST /api/v1/auth/login` con un email que no existe en la base de datos
- **THEN** el sistema retorna HTTP 401 Unauthorized con un mensaje genérico "Credenciales inválidas" (sin revelar si el email existe)

#### Scenario: Password incorrecto

- **WHEN** un usuario envía `POST /api/v1/auth/login` con un email registrado pero una contraseña incorrecta
- **THEN** el sistema retorna HTTP 401 Unauthorized con el mismo mensaje genérico "Credenciales inválidas"

#### Scenario: Campos faltantes

- **WHEN** un usuario envía `POST /api/v1/auth/login` sin el campo `email` o sin el campo `password`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con errores de validación por cada campo faltante

#### Scenario: Email con formato inválido

- **WHEN** un usuario envía `POST /api/v1/auth/login` con un email con formato inválido (ej: "notanemail")
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con error de validación en el campo `email`

### Requirement: Refresh token se persiste en base de datos

El sistema SHALL almacenar el refresh token en la tabla `refreshtoken` como SHA-256 hash (nunca el token en texto plano), junto con la fecha de expiración y la FK al usuario.

#### Scenario: Refresh token guardado tras login exitoso

- **WHEN** el login es exitoso
- **THEN** existe un registro en la tabla `refreshtoken` con `usuario_id` = id del usuario, `token_hash` = SHA-256 del token JWT emitido, `expires_at` = now + 7 días, `revoked_at` = NULL

#### Scenario: Refresh token hash es SHA-256

- **WHEN** se almacena el refresh token en BD
- **THEN** el campo `token_hash` contiene exactamente 64 caracteres hexadecimales (hex digest de SHA-256), nunca el JWT completo

### Requirement: Access token incluye el rol del usuario en el payload

El sistema SHALL incluir el claim `role` con el rol primario del usuario en el payload del access token JWT emitido en el login.

#### Scenario: Claim role presente en access token

- **WHEN** un usuario con rol CLIENT realiza un login exitoso
- **THEN** el payload del access token decodificado contiene `"role": "CLIENT"` además de los claims estándar (`sub`, `iat`, `exp`, `type`)

### Requirement: Rate limiting en el endpoint de login

El sistema SHALL limitar las peticiones al endpoint `POST /api/v1/auth/login` a un máximo de 5 requests por IP en una ventana deslizante de 15 minutos.

#### Scenario: Límite no superado — request permitido

- **WHEN** una IP realiza 5 o menos requests a `POST /api/v1/auth/login` en 15 minutos
- **THEN** cada request es procesado normalmente (ya sea 200, 401 o 422)

#### Scenario: Límite superado — request bloqueado

- **WHEN** una IP realiza el sexto request a `POST /api/v1/auth/login` dentro de la misma ventana de 15 minutos
- **THEN** el sistema retorna HTTP 429 Too Many Requests

#### Scenario: Ventana expirada — límite se resetea

- **WHEN** han pasado más de 15 minutos desde el primer request de la IP
- **THEN** el contador se resetea y la IP puede volver a hacer requests

### Requirement: TokenResponse incluye expires_in en segundos

El sistema SHALL retornar `expires_in` como entero en segundos correspondiente a la vida útil del access token.

#### Scenario: expires_in correcto

- **WHEN** el login es exitoso y `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- **THEN** `expires_in` en la respuesta es `1800` (30 × 60)
