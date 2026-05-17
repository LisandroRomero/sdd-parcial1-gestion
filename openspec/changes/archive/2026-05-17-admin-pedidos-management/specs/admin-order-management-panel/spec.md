## ADDED Requirements

### Requirement: Página admin dedicada con tabla de pedidos

La ruta `/admin/pedidos` SHALL renderizar `AdminPedidosPage`, una página con tabla de pedidos, filtros avanzados, y acciones rápidas inline. Reemplaza el comportamiento anterior donde `/admin/pedidos` mostraba la misma `PedidoListPage` de cards.

#### Scenario: Admin ve tabla en lugar de cards

- **WHEN** un usuario con rol ADMIN navega a `/admin/pedidos`
- **THEN** el sistema muestra la tabla de `AdminPedidosPage` (no las cards de `PedidoListPage`)

### Requirement: Ruta `/admin/pedidos/:id` para detalle admin

El sistema SHALL proveer la ruta `/admin/pedidos/:id` que renderiza `AdminPedidoDetailPage` con selector de estado destino, cancelación con motivo, y vista completa del pedido.

#### Scenario: Admin accede al detalle admin de un pedido

- **WHEN** un ADMIN navega a `/admin/pedidos/123`
- **THEN** el sistema muestra `AdminPedidoDetailPage` con la información completa del pedido y acciones admin

### Requirement: Botón "Avanzar estado" con selector en detalle admin

El sistema SHALL mostrar en `AdminPedidoDetailPage` un selector de estado destino con todas las transiciones válidas según la FSM, no solo el siguiente estado secuencial. Reemplaza el botón único "Avanzar a X" por un combo de selección + botón "Avanzar".

#### Scenario: Admin selecciona estado destino del selector

- **WHEN** un ADMIN está en el detalle admin de un pedido en estado CONFIRMADO
- **THEN** el selector muestra ["En preparación", "Cancelado"] como opciones disponibles

## MODIFIED Requirements

### Requirement: Ruta `/admin/pedidos` para gestión de pedidos

El sistema SHALL proveer la ruta `/admin/pedidos` accesible exclusivamente bajo `AdminRoute` (rol ADMIN) que muestra la **tabla de gestión de pedidos de `AdminPedidosPage`** con todos los pedidos del sistema, filtros avanzados y acciones rápidas.

#### Scenario: Admin accede al panel de gestión de pedidos

- **WHEN** un usuario con rol ADMIN navega a `/admin/pedidos`
- **THEN** el sistema muestra la **tabla de `AdminPedidosPage`** con todos los pedidos, filtros y acciones rápidas

#### Scenario: No-ADMIN no puede acceder a la ruta admin de pedidos

- **WHEN** un usuario sin rol ADMIN intenta navegar a `/admin/pedidos`
- **THEN** el sistema redirige al inicio o muestra acceso denegado

### Requirement: Botón "Avanzar estado" en detalle de pedido para gestores

El sistema SHALL mostrar un **selector de estado destino con confirmación** en `AdminPedidoDetailPage` cuando el usuario autenticado tiene rol GESTOR_PEDIDOS o ADMIN y el pedido tiene estados destino válidos en la FSM. El selector SHALL listar SOLO los estados destino válidos (no todos los estados del sistema). Al confirmar, SHALL invocar `PATCH /api/v1/pedidos/{id}/estado` con el estado seleccionado.

#### Scenario: Gestor selecciona y avanza estado desde selector

- **WHEN** un usuario con rol GESTOR_PEDIDOS accede al detalle admin de un pedido en estado CONFIRMADO
- **THEN** el sistema muestra un selector con opción "En preparación" y un botón "Avanzar"
- **WHEN** el Gestor selecciona "En preparación" y hace clic en "Avanzar"
- **THEN** el sistema llama a `PATCH /api/v1/pedidos/{id}/estado` con `{ nuevo_estado: "EN_PREP" }`, actualiza la vista y refresca el historial

#### Scenario: Sin selector en estado terminal

- **WHEN** un usuario ADMIN accede al detalle admin de un pedido en estado ENTREGADO o CANCELADO
- **THEN** el sistema NO muestra el selector ni botón de avance

#### Scenario: Error del backend se muestra al usuario

- **WHEN** el avance de estado falla (ej: transición inválida por concurrencia)
- **THEN** el sistema muestra un mensaje de error descriptivo sin recargar la página
