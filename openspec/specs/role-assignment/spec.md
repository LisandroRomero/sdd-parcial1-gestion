## Requirements

### Requirement: ADMIN puede asignar y modificar los roles de un usuario

El sistema SHALL proveer un endpoint `PUT /api/v1/usuarios/{id}/roles` accesible únicamente por usuarios con rol ADMIN, que reemplaza el conjunto completo de roles del usuario objetivo en una única transacción atómica.

#### Scenario: Asignación exitosa de roles

- **WHEN** un ADMIN autenticado envía `PUT /api/v1/usuarios/{id}/roles` con `{ "roles": ["CLIENT", "STOCK"] }` y el usuario con ese `id` existe
- **THEN** el sistema elimina todos los `UsuarioRol` actuales del usuario y crea los nuevos con `asignado_por_id` = id del ADMIN solicitante, retornando HTTP 200 con el `UserResponse` actualizado

#### Scenario: Lista de roles vacía es rechazada

- **WHEN** un ADMIN envía `PUT /api/v1/usuarios/{id}/roles` con `{ "roles": [] }`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity

#### Scenario: Rol inválido es rechazado

- **WHEN** un ADMIN envía `PUT /api/v1/usuarios/{id}/roles` con un código de rol inexistente (ej. `"SUPERUSER"`)
- **THEN** el sistema retorna HTTP 400 Bad Request

#### Scenario: RN-RB04 — ADMIN no puede quitarse su propio rol si es el único admin

- **WHEN** un ADMIN autenticado envía `PUT /api/v1/usuarios/{id}/roles` donde `id` es su propio `id`, la nueva lista NO incluye `"ADMIN"`, y no existen otros usuarios con el rol ADMIN en el sistema
- **THEN** el sistema retorna HTTP 400 Bad Request con mensaje "No puede quitarse el rol ADMIN: es el último administrador del sistema"

#### Scenario: No autenticado

- **WHEN** un cliente no autenticado envía `PUT /api/v1/usuarios/{id}/roles`
- **THEN** el sistema retorna HTTP 401 Unauthorized

#### Scenario: Usuario sin rol ADMIN intenta asignar roles

- **WHEN** un usuario autenticado sin rol ADMIN envía `PUT /api/v1/usuarios/{id}/roles`
- **THEN** el sistema retorna HTTP 403 Forbidden

#### Scenario: Usuario objetivo no existe

- **WHEN** un ADMIN envía `PUT /api/v1/usuarios/{id}/roles` con un `id` que no existe en la BD
- **THEN** el sistema retorna HTTP 404 Not Found
