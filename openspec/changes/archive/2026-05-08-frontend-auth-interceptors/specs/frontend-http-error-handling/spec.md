## ADDED Requirements

### Requirement: El frontend mapea errores HTTP a mensajes legibles por el usuario

El sistema SHALL proveer un helper `getErrorMessage(error)` que, dado un error de Axios, retorne un string con el mensaje apropiado: primero el `detail` del backend si está disponible, con fallback a mensajes predefinidos por código HTTP.

#### Scenario: Error con detail del backend usa ese mensaje

- **WHEN** el backend retorna un error con `{ "detail": "El email ya está registrado" }` y `getErrorMessage` lo recibe
- **THEN** retorna `"El email ya está registrado"`

#### Scenario: Error 400 sin detail retorna mensaje genérico

- **WHEN** se recibe un HTTP 400 sin campo `detail` en el body
- **THEN** `getErrorMessage` retorna `"Datos inválidos. Revisá los campos e intentá de nuevo."`

#### Scenario: Error 403 retorna mensaje de permisos

- **WHEN** se recibe un HTTP 403
- **THEN** `getErrorMessage` retorna `"No tenés permisos para esta acción."`

#### Scenario: Error 404 retorna mensaje de recurso no encontrado

- **WHEN** se recibe un HTTP 404
- **THEN** `getErrorMessage` retorna `"Recurso no encontrado."`

#### Scenario: Error 429 retorna mensaje de rate limit

- **WHEN** se recibe un HTTP 429
- **THEN** `getErrorMessage` retorna `"Demasiadas solicitudes. Esperá un momento e intentá de nuevo."`

#### Scenario: Error 500 retorna mensaje genérico de servidor

- **WHEN** se recibe un HTTP 500 o cualquier 5xx
- **THEN** `getErrorMessage` retorna `"Error interno del servidor. Intentá de nuevo más tarde."`

#### Scenario: Error de red (sin respuesta) retorna mensaje de conectividad

- **WHEN** la request falla sin respuesta del servidor (sin conexión, timeout)
- **THEN** `getErrorMessage` retorna `"Sin conexión. Verificá tu red e intentá de nuevo."`
