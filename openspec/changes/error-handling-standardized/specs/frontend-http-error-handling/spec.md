## MODIFIED Requirements

### Requirement: El frontend mapea errores HTTP a mensajes legibles por el usuario

El sistema SHALL proveer un helper `getErrorMessage(error)` que, dado un error de Axios, retorne un string con el mensaje apropiado, soportando el formato RFC 7807 canónico.

**Reason:** El backend migra a RFC 7807. El helper debe parsear `errors[0].message` (validación), `detail` (general), y mantener fallback por código HTTP. Se agregan códigos faltantes: 409, 422, 401.

#### Scenario: Error con errors array de validación usa el primer mensaje
- **WHEN** el backend retorna RFC 7807 con `{ "errors": [{ "field": "email", "message": "El email no es válido" }] }`
- **THEN** retorna `"El email no es válido"`

#### Scenario: Error sin errors array usa detail del backend
- **WHEN** el backend retorna RFC 7807 con `{ "detail": "El email ya está registrado" }` (sin `errors`)
- **THEN** retorna `"El email ya está registrado"`

#### Scenario: Error 400 sin detail ni errors retorna mensaje genérico
- **WHEN** se recibe un HTTP 400 sin campo `detail` ni `errors`
- **THEN** retorna `"Datos inválidos. Revisá los campos e intentá de nuevo."`

#### Scenario: Error 401 retorna mensaje de sesión expirada
- **WHEN** se recibe un HTTP 401 (no manejado por el interceptor de refresh)
- **THEN** retorna `"Sesión expirada. Iniciá sesión de nuevo."`

#### Scenario: Error 403 retorna mensaje de permisos
- **WHEN** se recibe un HTTP 403
- **THEN** retorna `"No tenés permisos para esta acción."`

#### Scenario: Error 404 retorna mensaje de recurso no encontrado
- **WHEN** se recibe un HTTP 404
- **THEN** retorna `"Recurso no encontrado."`

#### Scenario: Error 409 retorna mensaje de conflicto
- **WHEN** se recibe un HTTP 409
- **THEN** retorna `"Conflicto con el estado actual del recurso."`

#### Scenario: Error 422 retorna mensaje de validación
- **WHEN** se recibe un HTTP 422
- **THEN** retorna `"Error de validación. Revisá los datos ingresados."`

#### Scenario: Error 429 retorna mensaje de rate limit
- **WHEN** se recibe un HTTP 429
- **THEN** retorna `"Demasiadas solicitudes. Esperá un momento e intentá de nuevo."`

#### Scenario: Error 500 retorna mensaje genérico de servidor
- **WHEN** se recibe un HTTP 500 o cualquier 5xx
- **THEN** retorna `"Error interno del servidor. Intentá de nuevo más tarde."`

#### Scenario: Error de red (sin respuesta) retorna mensaje de conectividad
- **WHEN** la request falla sin respuesta del servidor
- **THEN** retorna `"Sin conexión. Verificá tu red e intentá de nuevo."`

#### Scenario: Error con requestId disponible se mantiene accesible
- **WHEN** el backend retorna RFC 7807 con `requestId`
- **THEN** el helper SHALL exponer el `requestId` para logging/debug (sin mostrarlo al usuario final)
