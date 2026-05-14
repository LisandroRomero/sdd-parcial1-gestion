## ADDED Requirements

### Requirement: Listar formas de pago con estado activo/inactivo

El sistema SHALL proveer `GET /api/v1/admin/configuracion/formas-de-pago` accesible solo para ADMIN que retorne todas las formas de pago con su campo `activo`. El campo `activo` SHALL indicar si la forma de pago está disponible para nuevos pedidos.

#### Scenario: Admin lista formas de pago

- **WHEN** un usuario con rol ADMIN realiza `GET /api/v1/admin/configuracion/formas-de-pago`
- **THEN** el sistema retorna una lista con `codigo`, `descripcion`, `activo` de cada forma de pago

#### Scenario: No-ADMIN recibe 403

- **WHEN** un usuario sin rol ADMIN realiza `GET /api/v1/admin/configuracion/formas-de-pago`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: Togglear habilitación de una forma de pago

El sistema SHALL proveer `PATCH /api/v1/admin/configuracion/formas-de-pago/{codigo}` accesible solo para ADMIN que actualice el campo `activo` de la forma de pago indicada.

#### Scenario: Admin deshabilita una forma de pago

- **WHEN** un usuario ADMIN realiza `PATCH /api/v1/admin/configuracion/formas-de-pago/RAPIPAGO` con `{ "activo": false }`
- **THEN** el sistema retorna HTTP 200 con la forma de pago actualizada (`activo: false`)

#### Scenario: Admin habilita una forma de pago previamente deshabilitada

- **WHEN** un usuario ADMIN realiza `PATCH /api/v1/admin/configuracion/formas-de-pago/RAPIPAGO` con `{ "activo": true }`
- **THEN** el sistema retorna HTTP 200 con `activo: true`

#### Scenario: Forma de pago no encontrada retorna 404

- **WHEN** un usuario ADMIN intenta togglear una forma de pago con código inexistente
- **THEN** el sistema retorna HTTP 404 Not Found

### Requirement: Panel frontend de configuración de formas de pago

El sistema SHALL proveer la ruta `/admin/configuracion` con una sección "Formas de pago" que muestre TARJETA, RAPIPAGO y PAGO_FACIL con su estado y un toggle para habilitarlas/deshabilitarlas.

#### Scenario: Admin ve el estado actual de las formas de pago

- **WHEN** un usuario ADMIN navega a `/admin/configuracion`
- **THEN** el sistema muestra una card por cada forma de pago con su nombre, descripción y estado (activo/inactivo)

#### Scenario: Admin cambia el estado de una forma de pago

- **WHEN** el Admin hace clic en el toggle de una forma de pago
- **THEN** el sistema llama a `PATCH /api/v1/admin/configuracion/formas-de-pago/{codigo}` y actualiza el badge de estado inmediatamente
