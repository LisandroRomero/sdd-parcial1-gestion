## ADDED Requirements

### Requirement: El frontend adjunta automáticamente el JWT a cada request autenticada

El sistema SHALL proveer una instancia Axios centralizada con un request interceptor que adjunte el header `Authorization: Bearer <token>` a todas las requests, tomando el access token del `authStore` en tiempo de ejecución.

#### Scenario: Request con token adjunta el header Authorization

- **WHEN** cualquier módulo del frontend realiza una llamada HTTP usando la instancia Axios centralizada y el `authStore` tiene un `token` activo
- **THEN** la request incluye el header `Authorization: Bearer <token>` con el access token actual

#### Scenario: Request sin token no adjunta el header

- **WHEN** la instancia Axios centralizada realiza una request y el `authStore` no tiene `token` (usuario no autenticado)
- **THEN** la request se envía sin header `Authorization`

#### Scenario: La instancia usa la baseURL de la variable de entorno

- **WHEN** se inicializa la instancia Axios
- **THEN** la baseURL es `VITE_API_BASE_URL` definida en el entorno, sin hardcodear la URL en el código

### Requirement: El frontend renueva el access token automáticamente ante un 401

El sistema SHALL proveer un response interceptor que, al recibir un HTTP 401, intente renovar el access token llamando a `POST /auth/refresh` con el `refreshToken` del store, actualice los tokens en el `authStore`, y reintente la request original de forma transparente para el usuario.

#### Scenario: Request 401 con refresh exitoso → request reintentada transparentemente

- **WHEN** una request recibe HTTP 401 y el `authStore` tiene un `refreshToken` válido
- **THEN** el interceptor llama a `POST /auth/refresh`, actualiza `authStore` con el nuevo par de tokens, y reintenta la request original con el nuevo access token, sin que el usuario perciba interrupción

#### Scenario: Request 401 con refresh fallido → logout y redirect a login

- **WHEN** una request recibe HTTP 401 y el refresh falla (refresh token expirado, revocado o ausente)
- **THEN** el interceptor llama a `authStore.logout()` y redirige al usuario a `/login`

#### Scenario: Múltiples requests 401 simultáneas → un solo refresh

- **WHEN** múltiples requests reciben HTTP 401 al mismo tiempo mientras ya hay un refresh en curso
- **THEN** solo se ejecuta una llamada a `POST /auth/refresh`; las demás requests se encolan y se reintentan con el nuevo token al completarse el refresh

#### Scenario: 401 en la propia request de refresh → no se hace refresh recursivo

- **WHEN** la request a `POST /auth/refresh` recibe un 401
- **THEN** el interceptor no intenta otro refresh, llama a `logout()` y redirige a `/login`
