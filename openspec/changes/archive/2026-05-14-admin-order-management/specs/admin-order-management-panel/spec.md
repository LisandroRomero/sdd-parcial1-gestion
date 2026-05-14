## ADDED Requirements

### Requirement: Botón "Avanzar estado" en detalle de pedido para gestores

El sistema SHALL mostrar un botón "Avanzar a [estado]" en `PedidoDetailPage` cuando el usuario autenticado tiene rol GESTOR_PEDIDOS o ADMIN y el pedido tiene un siguiente estado válido en la FSM. El botón SHALL invocar `PATCH /api/v1/pedidos/{id}/estado` con el estado destino. Las transiciones válidas son: CONFIRMADO→EN_PREPARACIÓN, EN_PREPARACIÓN→EN_CAMINO, EN_CAMINO→ENTREGADO.

#### Scenario: Gestor ve botón para avanzar un pedido CONFIRMADO

- **WHEN** un usuario con rol GESTOR_PEDIDOS accede al detalle de un pedido en estado CONFIRMADO
- **THEN** el sistema muestra el botón "Avanzar a En preparación"

#### Scenario: Gestor avanza el estado del pedido

- **WHEN** el Gestor hace clic en "Avanzar a En preparación"
- **THEN** el sistema llama a `PATCH /api/v1/pedidos/{id}/estado` con `{ nuevo_estado: "EN_PREP" }`, actualiza la vista y refresca el historial

#### Scenario: No se muestra botón en estado terminal

- **WHEN** un usuario ADMIN accede al detalle de un pedido en estado ENTREGADO o CANCELADO
- **THEN** el sistema NO muestra ningún botón de avance de estado

#### Scenario: No se muestra botón para CLIENT

- **WHEN** un usuario con rol CLIENT accede al detalle de su pedido en estado CONFIRMADO
- **THEN** el sistema NO muestra el botón "Avanzar estado" (ese rol no puede avanzar)

#### Scenario: Error del backend se muestra al usuario

- **WHEN** el avance de estado falla (ej: transición inválida por concurrencia)
- **THEN** el sistema muestra un mensaje de error descriptivo sin recargar la página

### Requirement: Ruta `/admin/pedidos` para gestión de pedidos

El sistema SHALL proveer la ruta `/admin/pedidos` accesible exclusivamente bajo `AdminRoute` (rol ADMIN) que muestra el listado completo de pedidos del sistema con todos los filtros y búsqueda disponibles.

#### Scenario: Admin accede al panel de gestión de pedidos

- **WHEN** un usuario con rol ADMIN navega a `/admin/pedidos`
- **THEN** el sistema muestra el listado de todos los pedidos (equivalente a `/pedidos` para ADMIN)

#### Scenario: No-ADMIN no puede acceder a la ruta admin de pedidos

- **WHEN** un usuario sin rol ADMIN intenta navegar a `/admin/pedidos`
- **THEN** el sistema redirige al inicio o muestra acceso denegado
