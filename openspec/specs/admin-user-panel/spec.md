## Requirements

### Requirement: Listar usuarios con búsqueda, filtro y paginación

El sistema SHALL proveer el endpoint `GET /api/v1/admin/usuarios` accesible exclusivamente para el rol ADMIN. La respuesta SHALL incluir: `id`, `nombre`, `apellido`, `email`, `activo`, `roles` (lista de códigos), `created_at`. Deberá soportar paginación `page/size`, búsqueda por nombre o email (`buscar`), y filtro por rol (`rol`).

#### Scenario: Admin lista todos los usuarios

- **WHEN** un usuario con rol ADMIN realiza `GET /api/v1/admin/usuarios`
- **THEN** el sistema retorna 200 con lista paginada de todos los usuarios del sistema

#### Scenario: Búsqueda por nombre o email

- **WHEN** se realiza `GET /api/v1/admin/usuarios?buscar=juan`
- **THEN** el sistema retorna solo los usuarios cuyo nombre o email contiene "juan" (case-insensitive)

#### Scenario: Filtro por rol

- **WHEN** se realiza `GET /api/v1/admin/usuarios?rol=ADMIN`
- **THEN** el sistema retorna solo los usuarios que tienen el rol ADMIN asignado

#### Scenario: No-ADMIN recibe 403

- **WHEN** un usuario con rol CLIENT o GESTOR_PEDIDOS realiza `GET /api/v1/admin/usuarios`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: Editar datos y rol de usuario

El sistema SHALL proveer el endpoint `PUT /api/v1/admin/usuarios/{id}` para que ADMIN pueda modificar `nombre`, `apellido`, `email` y `roles` de cualquier usuario. Al cambiar el rol SHALL invalidar todos los refresh tokens del usuario afectado. SHALL respetar RN-RB04: no permitir quitar el rol ADMIN si el usuario es el último administrador del sistema.

#### Scenario: Admin cambia el rol de un usuario

- **WHEN** un ADMIN realiza `PUT /api/v1/admin/usuarios/42` con `{ roles: ["GESTOR_PEDIDOS"] }`
- **THEN** el sistema actualiza los roles del usuario y revoca todos sus refresh tokens activos

#### Scenario: No se puede degradar al último ADMIN

- **WHEN** un ADMIN intenta quitar el rol ADMIN al único administrador restante del sistema
- **THEN** el sistema retorna HTTP 400 con mensaje "No se puede quitar el rol ADMIN: es el último administrador"

#### Scenario: Editar datos básicos sin cambiar rol

- **WHEN** un ADMIN realiza `PUT /api/v1/admin/usuarios/42` con `{ nombre: "Juan Carlos" }` sin campo roles
- **THEN** el sistema actualiza el nombre y no revoca refresh tokens

#### Scenario: Usuario no encontrado

- **WHEN** un ADMIN intenta editar un usuario con `id` que no existe
- **THEN** el sistema retorna HTTP 404 Not Found

### Requirement: Activar o desactivar usuario

El sistema SHALL proveer el endpoint `PATCH /api/v1/admin/usuarios/{id}/estado` para activar o desactivar un usuario. Al desactivar SHALL revocar todos los refresh tokens activos del usuario. El campo `activo` SHALL persistirse en la tabla `usuario`.

#### Scenario: Admin desactiva un usuario

- **WHEN** un ADMIN realiza `PATCH /api/v1/admin/usuarios/42/estado` con `{ activo: false }`
- **THEN** el sistema marca `activo=false` en el usuario y revoca todos sus refresh tokens

#### Scenario: Usuario desactivado no puede re-autenticarse

- **WHEN** un usuario con `activo=false` intenta realizar un login con credenciales válidas
- **THEN** el sistema retorna HTTP 403 con mensaje "Cuenta desactivada" (ver spec user-login)

#### Scenario: Admin activa un usuario previamente desactivado

- **WHEN** un ADMIN realiza `PATCH /api/v1/admin/usuarios/42/estado` con `{ activo: true }`
- **THEN** el sistema marca `activo=true` y el usuario puede volver a autenticarse

### Requirement: Panel frontend de gestión de usuarios

El sistema SHALL proveer la ruta `/admin/usuarios` accesible solo para usuarios con rol ADMIN. La página SHALL mostrar una tabla con: nombre, email, roles, estado (activo/inactivo), fecha de registro. SHALL incluir: campo de búsqueda, filtro por rol, paginación, y acciones por fila (editar datos/rol, toggle activo).

#### Scenario: Admin accede al panel de usuarios

- **WHEN** un usuario con rol ADMIN navega a `/admin/usuarios`
- **THEN** ve una tabla con todos los usuarios del sistema, paginada de 20 en 20

#### Scenario: Búsqueda filtra la tabla

- **WHEN** el Admin escribe en el campo de búsqueda
- **THEN** la tabla se actualiza mostrando solo los usuarios que coinciden

#### Scenario: Toggle de estado cambia activo inmediatamente

- **WHEN** el Admin hace clic en el toggle de estado de un usuario
- **THEN** el sistema llama a `PATCH /admin/usuarios/{id}/estado` y refresca la tabla

#### Scenario: No-ADMIN es redirigido

- **WHEN** un usuario con rol CLIENT navega a `/admin/usuarios`
- **THEN** el sistema redirige al inicio o muestra 403
