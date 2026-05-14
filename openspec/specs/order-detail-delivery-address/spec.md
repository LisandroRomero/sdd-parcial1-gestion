### Requirement: Mostrar dirección de entrega en detalle de pedido

El sistema SHALL mostrar una sección "Dirección de entrega" en `PedidoDetailPage` con los datos de la dirección asociada al pedido al momento de la consulta. Los campos SHALL incluir: calle, número, piso/departamento (si existe), ciudad, provincia y código postal (si existe).

#### Scenario: Detalle muestra dirección asociada al pedido

- **WHEN** un usuario autenticado consulta el detalle de un pedido que tiene `direccion_id` asignado
- **THEN** el sistema muestra una sección "Dirección de entrega" con calle, número, ciudad y provincia

#### Scenario: Detalle muestra piso/depto si existe

- **WHEN** la dirección tiene `piso` o `departamento` no nulos
- **THEN** el sistema muestra el piso/departamento en la sección de dirección

#### Scenario: Dirección ausente no bloquea el detalle

- **WHEN** el campo `direccion` es nulo en la respuesta del backend
- **THEN** la sección "Dirección de entrega" no se renderiza (no se muestra error)
