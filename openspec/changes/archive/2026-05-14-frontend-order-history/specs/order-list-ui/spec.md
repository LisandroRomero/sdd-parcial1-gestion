## ADDED Requirements

### Requirement: OrderCard muestra cantidad de ítems

El `OrderCard` SHALL mostrar la cantidad de ítems del pedido (`cantidad_items`) junto a la fecha y costo de envío.

#### Scenario: Card muestra cantidad de ítems

- **WHEN** se renderiza un `OrderCard` con un pedido que tiene `cantidad_items = 3`
- **THEN** el card muestra "3 ítems" o equivalente visible al usuario

#### Scenario: Card con un solo ítem usa singular

- **WHEN** se renderiza un `OrderCard` con `cantidad_items = 1`
- **THEN** el card muestra "1 ítem" (singular)

### Requirement: Input de búsqueda en OrderFilters

`OrderFilters` SHALL proveer un input de búsqueda que permita filtrar pedidos por número de pedido. El valor ingresado SHALL enviarse como query param `buscar` al backend.

#### Scenario: Búsqueda por número de pedido

- **WHEN** el usuario escribe "42" en el input de búsqueda y presiona Enter o el campo pierde el foco
- **THEN** el sistema envía `GET /api/v1/pedidos/?buscar=42&page=1&size=20` y muestra solo los pedidos que coinciden

#### Scenario: Limpiar búsqueda restaura el listado completo

- **WHEN** el usuario borra el texto del input de búsqueda
- **THEN** el query param `buscar` se elimina y el sistema carga el listado completo

## MODIFIED Requirements

### Requirement: Página de listado de pedidos con paginación

El sistema SHALL proveer una página `/pedidos` que muestre los pedidos del usuario en formato de cards paginadas. Para usuarios CLIENTE, la página SHALL mostrar solo sus propios pedidos con el título "Mis Pedidos". Para usuarios ADMIN y GESTOR_PEDIDOS, SHALL mostrar todos los pedidos del sistema con el título "Pedidos". La paginación SHALL usar el formato `page/size` (page 1-indexed) con metadata `{ items, total, page, size, pages }`.

#### Scenario: CLIENTE ve sus pedidos paginados con título "Mis Pedidos"

- **WHEN** un usuario con rol `CLIENTE` navega a `/pedidos`
- **THEN** el sistema muestra el título "Mis Pedidos" y solo los pedidos donde `usuario_id` coincide con el usuario autenticado, paginados en cards

#### Scenario: ADMIN ve todos los pedidos con título "Pedidos"

- **WHEN** un usuario con rol `ADMIN` navega a `/pedidos`
- **THEN** el sistema muestra el título "Pedidos" y todos los pedidos del sistema paginados

#### Scenario: GESTOR_PEDIDOS ve todos los pedidos con título "Pedidos"

- **WHEN** un usuario con rol `GESTOR_PEDIDOS` navega a `/pedidos`
- **THEN** el sistema muestra el título "Pedidos" y todos los pedidos del sistema paginados

#### Scenario: Navegación entre páginas

- **WHEN** el usuario hace clic en "Siguiente" en la paginación
- **THEN** el sistema carga la siguiente página de resultados vía `GET /api/v1/pedidos/?page=2&size=20`

#### Scenario: Página vacía muestra estado vacío

- **WHEN** el usuario no tiene pedidos
- **THEN** el sistema muestra un mensaje "No tienes pedidos aún" con un botón para ir al catálogo

#### Scenario: Filtrar por estado

- **WHEN** el usuario selecciona "PENDIENTE" en el filtro de estado
- **THEN** el sistema envía `GET /api/v1/pedidos/?estado=PENDIENTE&page=1&size=20` y muestra solo pedidos pendientes

#### Scenario: Filtrar por rango de fechas

- **WHEN** el usuario selecciona un rango de fechas `2026-01-01` a `2026-01-31`
- **THEN** el sistema envía `GET /api/v1/pedidos/?fecha_desde=2026-01-01&fecha_hasta=2026-01-31&page=1&size=20`

#### Scenario: Combinar filtros con búsqueda

- **WHEN** el usuario selecciona estado "CONFIRMADO" y escribe "5" en el input de búsqueda
- **THEN** el sistema envía `GET /api/v1/pedidos/?estado=CONFIRMADO&buscar=5&page=1&size=20`

#### Scenario: Limpiar filtros

- **WHEN** el usuario hace clic en "Limpiar filtros"
- **THEN** todos los filtros (incluido `buscar`) se resetean y se muestra la página 1 sin filtros
