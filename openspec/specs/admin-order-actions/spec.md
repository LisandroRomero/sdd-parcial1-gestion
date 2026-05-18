## Requirements

### Requirement: Menú de acciones rápidas en tabla admin

Cada fila de la tabla de pedidos SHALL tener un menú desplegable (tres puntos) con acciones contextuales según el estado del pedido: "Ver detalle" (navega a `/admin/pedidos/{id}`), "Avanzar estado" (permite seleccionar el estado destino), y "Cancelar pedido" (abre modal con motivo).

#### Scenario: Admin usa acción rápida para avanzar estado desde la tabla

- **WHEN** el admin hace clic en el menú de acciones de un pedido en estado CONFIRMADO y selecciona "Avanzar a En preparación"
- **THEN** el sistema llama a `PATCH /api/v1/pedidos/{id}/estado` con `{ nuevo_estado: "EN_PREP" }` y actualiza la fila sin recargar la página

#### Scenario: Admin cancela pedido desde la tabla

- **WHEN** el admin hace clic en "Cancelar pedido" desde el menú de acciones de un pedido no terminal
- **THEN** el sistema abre un modal para seleccionar motivo de cancelación

#### Scenario: Acciones deshabilitadas para pedidos terminales

- **WHEN** el pedido está en estado ENTREGADO o CANCELADO
- **THEN** el menú de acciones solo muestra "Ver detalle"

### Requirement: Selector de estado destino en detalle admin

En `AdminPedidoDetailPage`, el sistema SHALL mostrar un selector (select) con todos los estados destino válidos según la FSM para el estado actual del pedido. Al seleccionar un estado y confirmar, se invoca `PATCH /api/v1/pedidos/{id}/estado`.

#### Scenario: Admin ve selector de estados válidos

- **WHEN** un ADMIN accede al detalle de un pedido en estado CONFIRMADO
- **THEN** el selector muestra las opciones "En preparación" y "Cancelado"

#### Scenario: Admin cambia a un estado no secuencial

- **WHEN** un ADMIN selecciona "En camino" para un pedido en CONFIRMADO
- **THEN** el sistema envía `PATCH /api/v1/pedidos/{id}/estado` con `{ nuevo_estado: "EN_CAMINO" }` y el backend valida la transición

#### Scenario: Error de transición inválida se muestra al admin

- **WHEN** el backend rechaza la transición (ej: por concurrencia)
- **THEN** el sistema muestra un mensaje de error descriptivo

### Requirement: Cancelación con motivo en admin

El sistema SHALL permitir a ADMIN y PEDIDOS cancelar pedidos con selección de motivo obligatorio desde el detalle admin o desde la tabla.

#### Scenario: Admin cancela pedido con motivo desde el detalle

- **WHEN** un ADMIN hace clic en "Cancelar pedido" en el detalle de un pedido en estado CONFIRMADO, selecciona "Cliente solicitó cancelación" como motivo, y confirma
- **THEN** el sistema llama a `DELETE /api/v1/pedidos/{id}?motivo=Cliente solicitó cancelación` y actualiza la vista
