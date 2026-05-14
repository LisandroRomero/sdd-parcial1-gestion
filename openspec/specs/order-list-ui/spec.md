### Requirement: Página de listado de pedidos con paginación

El sistema SHALL proveer una página `/pedidos` que muestre los pedidos del usuario en formato de cards paginadas. Para usuarios CLIENTE, la página SHALL mostrar solo sus propios pedidos. Para usuarios ADMIN y GESTOR_PEDIDOS, SHALL mostrar todos los pedidos del sistema.

La paginación SHALL usar el formato `page/size` (page 1-indexed) con metadata `{ items, total, page, size, pages }`.

#### Scenario: CLIENTE ve sus pedidos paginados
- **WHEN** un usuario con rol `CLIENTE` navega a `/pedidos`
- **THEN** el sistema muestra solo los pedidos donde `usuario_id` coincide con el usuario autenticado, paginados en cards

#### Scenario: ADMIN ve todos los pedidos
- **WHEN** un usuario con rol `ADMIN` navega a `/pedidos`
- **THEN** el sistema muestra todos los pedidos del sistema paginados

#### Scenario: Navegación entre páginas
- **WHEN** el usuario hace clic en "Siguiente" en la paginación
- **THEN** el sistema carga la siguiente página de resultados vía `GET /api/v1/pedidos/?page=2&size=20`

#### Scenario: Página vacía muestra estado vacío
- **WHEN** el usuario no tiene pedidos
- **THEN** el sistema muestra un mensaje "No tienes pedidos aún" con un botón para ir al catálogo

### Requirement: Card de pedido (OrderCard)

Cada pedido en el listado SHALL mostrar: ID del pedido (formateado), badge de estado con color, monto total, fecha de creación formateada, y costo de envío. El card SHALL ser clickeable y navegar al detalle del pedido.

#### Scenario: Card muestra datos del pedido
- **WHEN** se renderiza un card de pedido
- **THEN** muestra `id`, badge de `estado_actual` con color semántico, `total`, `created_at` en formato legible, y `costo_envio`

#### Scenario: Click en card navega al detalle
- **WHEN** el usuario hace clic en un card de pedido
- **THEN** el sistema navega a `/pedidos/{id}` mostrando el detalle completo del pedido

#### Scenario: Badge de estado usa color semántico
- **WHEN** se muestra el badge de estado en la card
- **THEN** el color del badge corresponde al estado del pedido según el mapa de colores definido en `constants.ts`

### Requirement: Filtros de listado

El listado SHALL proveer filtros por estado y rango de fechas. Los filtros SHALL aplicarse server-side como query params.

#### Scenario: Filtrar por estado
- **WHEN** el usuario selecciona "PENDIENTE" en el filtro de estado
- **THEN** el sistema envía `GET /api/v1/pedidos/?estado=PENDIENTE&page=1&size=20` y muestra solo pedidos pendientes

#### Scenario: Filtrar por rango de fechas
- **WHEN** el usuario selecciona un rango de fechas `2026-01-01` a `2026-01-31`
- **THEN** el sistema envía `GET /api/v1/pedidos/?fecha_desde=2026-01-01&fecha_hasta=2026-01-31&page=1&size=20`

#### Scenario: Combinar filtros
- **WHEN** el usuario selecciona estado "CONFIRMADO" y rango de fechas
- **THEN** ambos filtros se envían como query params simultáneamente

#### Scenario: Limpiar filtros
- **WHEN** el usuario hace clic en "Limpiar filtros"
- **THEN** todos los filtros se resetear y se muestra la página 1 sin filtros

### Requirement: Sidebar/Navegación con entrada "Mis Pedidos"

El menú de navegación del usuario CLIENTE SHALL incluir una entrada "Mis Pedidos" que navegue a `/pedidos`. Para ADMIN y GESTOR_PEDIDOS, la entrada SHALL decir "Pedidos".

#### Scenario: CLIENTE ve "Mis Pedidos" en navegación
- **WHEN** un usuario CLIENTE abre el menú de navegación
- **THEN** ve una entrada "Mis Pedidos" que navega a `/pedidos`

#### Scenario: ADMIN/GESTOR_PEDIDOS ve "Pedidos" en navegación
- **WHEN** un usuario ADMIN o GESTOR_PEDIDOS abre el menú de navegación
- **THEN** ve una entrada "Pedidos" que navega a `/pedidos`

### Requirement: Ruteo protegido para páginas de pedidos

Las rutas `/pedidos` y `/pedidos/:id` SHALL estar protegidas por autenticación. Usuarios no autenticados SHALL ser redirigidos al login.

#### Scenario: Usuario no autenticado es redirigido
- **WHEN** un usuario no autenticado intenta acceder a `/pedidos`
- **THEN** el sistema redirige a la página de login

#### Scenario: Usuario autenticado accede sin problemas
- **WHEN** un usuario autenticado navega a `/pedidos`
- **THEN** el sistema muestra la página de listado sin redirecciones

### Requirement: Estados de carga y error en listado

El listado SHALL manejar estados loading, error, y empty de forma explícita.

#### Scenario: Loading muestra spinner/skeleton
- **WHEN** el listado está cargando los pedidos
- **THEN** se muestran indicadores de carga (skeleton cards o spinner)

#### Scenario: Error en carga muestra mensaje
- **WHEN** la carga de pedidos falla (error de red, 500, etc.)
- **THEN** se muestra un mensaje de error con botón "Reintentar"

#### Scenario: Refetch manual desde estado de error
- **WHEN** el usuario hace clic en "Reintentar"
- **THEN** el sistema reintenta la carga de pedidos
