## ADDED Requirements

### Requirement: Cuenta desactivada retorna 403 en login

El sistema SHALL verificar el campo `activo` del usuario después de validar las credenciales. Si `activo=False`, SHALL retornar HTTP 403 con el mensaje "Cuenta desactivada" sin emitir tokens.

#### Scenario: Usuario desactivado intenta login con credenciales correctas

- **WHEN** un usuario con `activo=False` envía `POST /api/v1/auth/login` con email y password válidos
- **THEN** el sistema retorna HTTP 403 Forbidden con detalle "Cuenta desactivada" y no emite access token ni refresh token

#### Scenario: Usuario activo continúa el flujo normal

- **WHEN** un usuario con `activo=True` envía `POST /api/v1/auth/login` con credenciales válidas
- **THEN** el flujo de login continúa normalmente y se emiten los tokens (sin cambio de comportamiento)
