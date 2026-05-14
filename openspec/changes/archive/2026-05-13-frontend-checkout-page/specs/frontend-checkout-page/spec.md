## ADDED Requirements

### Requirement: Página de checkout con ruta protegida

El frontend SHALL implementar una página `/checkout` accesible solo para usuarios autenticados con rol CLIENTE. La ruta SHALL ser hija de `/` y usar `ProtectedRoute` con verificación de rol.

#### Scenario: Navegar a checkout autenticado como CLIENTE

- **WHEN** un usuario autenticado con rol CLIENTE navega a `/checkout`
- **THEN** la página de checkout SHALL renderizarse

#### Scenario: Navegar a checkout sin autenticación

- **WHEN** un usuario no autenticado navega a `/checkout`
- **THEN** el sistema SHALL redirigir al login

#### Scenario: Navegar a checkout con rol distinto a CLIENTE

- **WHEN** un usuario autenticado con rol ADMIN, GESTOR_STOCK o GESTOR_PEDIDOS navega a `/checkout`
- **THEN** el sistema SHALL redirigir al dashboard correspondiente o mostrar 403

---

### Requirement: Resumen del carrito en checkout

La página de checkout SHALL mostrar un resumen completo del carrito con:
- Lista de items con nombre, precio unitario, cantidad, ingredientes excluidos y subtotal
- Total general del pedido
- Si el carrito está vacío, mostrar mensaje "Tu carrito está vacío" con botón "Ir al catálogo"

#### Scenario: Checkout con items en el carrito

- **WHEN** el usuario navega a `/checkout` con items en `useCartStore`
- **THEN** SHALL mostrarse cada item con nombre, cantidad, precio unitario y subtotal
- **THEN** SHALL mostrarse el total general del pedido

#### Scenario: Checkout con carrito vacío

- **WHEN** el usuario navega a `/checkout` con `isCartEmpty = true`
- **THEN** SHALL mostrarse mensaje "Tu carrito está vacío"
- **THEN** SHALL mostrarse un botón "Ir al catálogo" que navega a la página de productos

---

### Requirement: Selector de dirección de entrega

La página de checkout SHALL mostrar un selector de dirección de entrega que liste las direcciones guardadas del usuario. El usuario SHALL poder seleccionar UNA dirección como destino del pedido. Si no hay direcciones guardadas, SHALL mostrar mensaje con CTA para ir a gestión de direcciones.

#### Scenario: Seleccionar dirección existente

- **WHEN** el usuario tiene una o más direcciones guardadas
- **THEN** SHALL mostrarse un listado seleccionable de direcciones (alias, calle, número, ciudad)
- **THEN** el usuario puede hacer clic en una dirección para seleccionarla
- **THEN** la dirección seleccionada SHALL mostrarse visualmente destacada

#### Scenario: Sin direcciones guardadas

- **WHEN** el usuario no tiene direcciones guardadas
- **THEN** SHALL mostrarse mensaje "No tenés direcciones guardadas"
- **THEN** SHALL mostrarse un botón "Ir a mi perfil" que navega a `/perfil`
- **THEN** el botón "Confirmar pedido" SHALL estar deshabilitado

---

### Requirement: Confirmar pedido

La página de checkout SHALL tener un botón "Confirmar pedido" que:
- Está deshabilitado si `isCartEmpty` o no hay dirección seleccionada
- Al hacer clic, envía `POST /api/v1/pedidos` con los items del carrito y la dirección seleccionada
- Muestra un estado de carga (spinner) mientras la petición está en curso
- En caso de error, muestra el mensaje de error y permite reintentar

El payload de `POST /api/v1/pedidos` SHALL incluir:
- `detalles: { producto_id, cantidad }[]` derivado de `useCartStore().items`
- `direccion_id: number` de la dirección seleccionada

#### Scenario: Confirmar pedido exitosamente

- **WHEN** el usuario tiene items en el carrito y una dirección seleccionada
- **WHEN** hace clic en "Confirmar pedido"
- **AND** `POST /api/v1/pedidos` responde con `201 Created`
- **THEN** el sistema SHALL navegar a la pantalla de confirmación
- **THEN** `useCartStore().clearCart()` SHALL ser llamado

#### Scenario: Error al confirmar pedido — stock insuficiente

- **WHEN** `POST /api/v1/pedidos` responde con error `PEDIDO_STOCK_INSUFICIENTE`
- **THEN** SHALL mostrarse mensaje de error específico indicando el producto y stock disponible
- **THEN** el botón "Confirmar pedido" SHALL estar habilitado para reintentar

#### Scenario: Error al confirmar pedido — dirección inválida

- **WHEN** `POST /api/v1/pedidos` responde con error `PEDIDO_DIRECCION_NOT_FOUND` o `PEDIDO_DIRECCION_NO_AUTORIZADA`
- **THEN** SHALL mostrarse mensaje de error indicando que la dirección no es válida
- **THEN** el usuario SHALL poder seleccionar otra dirección

#### Scenario: Error al confirmar pedido — producto no disponible

- **WHEN** `POST /api/v1/pedidos` responde con error `PEDIDO_PRODUCTO_NO_DISPONIBLE`
- **THEN** SHALL mostrarse mensaje de error indicando qué producto no está disponible
- **THEN** el botón "Confirmar pedido" SHALL estar deshabilitado (requiere volver al carrito)

#### Scenario: Botón deshabilitado sin dirección seleccionada

- **WHEN** el usuario tiene items en el carrito pero no ha seleccionado dirección
- **THEN** el botón "Confirmar pedido" SHALL estar deshabilitado

#### Scenario: Botón deshabilitado con carrito vacío

- **WHEN** `isCartEmpty === true`
- **THEN** el botón "Confirmar pedido" SHALL estar deshabilitado

---

### Requirement: Pantalla de confirmación de pedido

Después de crear un pedido exitosamente, el sistema SHALL mostrar una pantalla de confirmación con:
- Ícono de éxito (check verde)
- Número de pedido (`pedido.id`)
- Mensaje "¡Pedido confirmado!"
- Resumen breve (cantidad de items, total, dirección de entrega)
- Botón "Volver al catálogo" que navega a la página de productos

#### Scenario: Confirmación muestra número de pedido

- **WHEN** el pedido se crea exitosamente con `pedido.id = 42`
- **THEN** la pantalla de confirmación SHALL mostrar "Pedido #42"
- **THEN** SHALL mostrar "¡Pedido confirmado!"

#### Scenario: Navegar al catálogo desde confirmación

- **WHEN** el usuario hace clic en "Volver al catálogo"
- **THEN** el sistema navega a la página de productos
