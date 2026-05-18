## Requirements

### Requirement: Vista tabular de pedidos para admin

El sistema SHALL proveer una página en `/admin/pedidos` con una tabla que liste todos los pedidos del sistema, accesible exclusivamente para usuarios con rol ADMIN o PEDIDOS. La tabla SHALL mostrar columnas de: ID del pedido, nombre del usuario, estado actual (con badge de color), total, cantidad de ítems, fecha de creación, y acciones.

#### Scenario: Admin ve la tabla de pedidos

- **WHEN** un usuario con rol ADMIN navega a `/admin/pedidos`
- **THEN** el sistema muestra una tabla con todos los pedidos ordenados por fecha descendente

#### Scenario: Gestor de pedidos ve la tabla

- **WHEN** un usuario con rol GESTOR_PEDIDOS navega a `/admin/pedidos`
- **THEN** el sistema muestra la misma tabla de pedidos

#### Scenario: Columna de estado con badge de color

- **WHEN** la tabla renderiza un pedido
- **THEN** la columna "Estado" muestra un badge con el color correspondiente según `statusColors`

#### Scenario: Columna de acciones

- **WHEN** la tabla renderiza un pedido
- **THEN** la última columna muestra un menú desplegable con acciones disponibles según el estado actual

### Requirement: Filtros avanzados en tabla admin

El sistema SHALL proveer los siguientes filtros en la tabla admin: búsqueda por ID o nombre de usuario, filtro por estado (select con todos los estados), filtro por rango de fechas (desde/hasta), y paginación.

#### Scenario: Búsqueda por nombre de usuario

- **WHEN** el admin escribe "Juan" en el campo de búsqueda
- **THEN** la tabla muestra solo pedidos cuyo usuario se llama "Juan" o cuyo ID coincide

#### Scenario: Filtro por estado

- **WHEN** el admin selecciona "CONFIRMADO" en el filtro de estado
- **THEN** la tabla muestra solo pedidos en estado CONFIRMADO

#### Scenario: Paginación

- **WHEN** hay más de 20 pedidos
- **THEN** la tabla muestra paginación con botones de página

### Requirement: Ordenamiento de columnas

El sistema SHALL permitir ordenar la tabla por ID, total, y fecha de creación, alternando entre ascendente y descendente al hacer clic en el encabezado de la columna.

#### Scenario: Ordenar por total descendente

- **WHEN** el admin hace clic en "Total" dos veces
- **THEN** la tabla se ordena por total de mayor a menor
