## MODIFIED Requirements

### Requirement: Pantalla de confirmación de pedido

Después de crear un pedido exitosamente, el sistema SHALL mostrar una pantalla de confirmación con:
- Ícono de éxito (check verde)
- Número de pedido (`pedido.id`)
- Mensaje "¡Pedido confirmado!"
- Resumen breve (cantidad de items, total, dirección de entrega)
- Botón "Volver al catálogo" que navega a la página de productos
- Enlace "Ver detalle del pedido" que navega a la página de detalle del pedido (ej: `/pedidos/{id}`)

#### Scenario: Confirmación muestra número de pedido
- **WHEN** el pedido se crea exitosamente con `pedido.id = 42`
- **THEN** la pantalla de confirmación SHALL mostrar "Pedido #42"
- **THEN** SHALL mostrar "¡Pedido confirmado!"

#### Scenario: Navegar al catálogo desde confirmación
- **WHEN** el usuario hace clic en "Volver al catálogo"
- **THEN** el sistema navega a la página de productos

#### Scenario: Navegar al detalle del pedido desde confirmación
- **WHEN** el usuario hace clic en "Ver detalle del pedido"
- **THEN** el sistema navega a `/pedidos/{id}` donde `id` es el `pedido.id` del pedido recién creado

#### Scenario: Ambos links son visibles simultáneamente
- **WHEN** la pantalla de confirmación se renderiza
- **THEN** tanto "Volver al catálogo" como "Ver detalle del pedido" SHALL estar visibles
- **THEN** "Ver detalle del pedido" SHALL mostrarse como un link o botón secundario (outline style)
- **THEN** "Volver al catálogo" SHALL mostrarse como el botón primario
