## ADDED Requirements

### Requirement: Selector de estado destino en tabla admin

La tabla de pedidos en `AdminPedidosPage` SHALL mostrar un selector de estado destino (con múltiples opciones) cuando el admin hace clic en "Avanzar estado" desde el menú de acciones, en lugar de un avance lineal fijo. El selector SHALL ofrecer todos los estados destino válidos según `getAdminNextStates()`.

#### Scenario: Admin selecciona estado destino desde la tabla
- **WHEN** el admin hace clic en "Avanzar estado" para un pedido en PENDIENTE
- **THEN** se muestra un selector inline con opciones "Confirmado" y "Cancelado", y al seleccionar y confirmar se invoca `PATCH /api/v1/pedidos/{id}/estado` con el estado elegido

#### Scenario: Admin avanza de PENDIENTE a CONFIRMADO desde la tabla
- **WHEN** el admin selecciona "CONFIRMADO" en el selector y confirma
- **THEN** el sistema llama a `PATCH /api/v1/pedidos/{id}/estado` con `{ nuevo_estado: "CONFIRMADO" }`

#### Scenario: Tabla muestra acciones para PENDIENTE
- **WHEN** la tabla renderiza un pedido en estado PENDIENTE
- **THEN** el menú de acciones incluye "Avanzar estado" (antes no aparecía)

#### Scenario: Estado terminal no muestra "Avanzar estado"
- **WHEN** la tabla renderiza un pedido en estado ENTREGADO o CANCELADO
- **THEN** el menú de acciones solo muestra "Ver detalle" y "Cancelar pedido" (si aplica)
