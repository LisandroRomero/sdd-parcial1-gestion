### Requirement: Cliente puede crear un pedido
El sistema SHALL permitir a un usuario autenticado con rol CLIENTE crear un pedido a partir de una lista de productos y una dirección de entrega de su propiedad. La operación SHALL ser atómica: o todos los recursos se persisten correctamente o ninguno se persiste.

#### Scenario: Creación exitosa con stock suficiente
- **WHEN** el cliente autenticado envía `POST /api/v1/pedidos` con `direccion_id` válida (de su propiedad) y al menos un `DetallePedidoCreate` con `producto_id` válido, `cantidad >= 1`, y stock suficiente
- **THEN** el sistema crea el `Pedido` con `estado_actual = "PENDIENTE"`, crea cada `DetallePedido` con `nombre_snapshot` y `precio_snapshot` copiados del `Producto`, descuenta `stock_cantidad` en cada `Producto`, y devuelve `201 Created` con el `PedidoRead` completo incluyendo sus detalles

#### Scenario: Carrito vacío
- **WHEN** el cliente envía la solicitud con `detalles = []`
- **THEN** el sistema devuelve `400 Bad Request` con error `PEDIDO_CARRITO_VACIO`

#### Scenario: Dirección no pertenece al usuario
- **WHEN** el cliente envía `direccion_id` de una dirección que pertenece a otro usuario
- **THEN** el sistema devuelve `403 Forbidden` con error `PEDIDO_DIRECCION_NO_AUTORIZADA` y no persiste ningún cambio

#### Scenario: Dirección no existe o fue eliminada
- **WHEN** el cliente envía un `direccion_id` que no existe o tiene `deleted_at` no nulo
- **THEN** el sistema devuelve `404 Not Found` con error `PEDIDO_DIRECCION_NOT_FOUND`

#### Scenario: Stock insuficiente en un producto
- **WHEN** al menos un producto en `detalles` tiene `stock_cantidad < cantidad` solicitada
- **THEN** el sistema devuelve `422 Unprocessable Entity` con error `PEDIDO_STOCK_INSUFICIENTE` indicando el `producto_id` y el stock disponible, y no persiste ningún cambio (rollback total)

#### Scenario: Producto inactivo o eliminado
- **WHEN** al menos un `producto_id` en `detalles` tiene `deleted_at` no nulo o `disponible = False`
- **THEN** el sistema devuelve `422 Unprocessable Entity` con error `PEDIDO_PRODUCTO_NO_DISPONIBLE` indicando el `producto_id`, y no persiste ningún cambio

#### Scenario: Rol no autorizado (no CLIENTE)
- **WHEN** un usuario autenticado con rol distinto a CLIENTE (ej: ADMIN, GESTOR_STOCK, GESTOR_PEDIDOS) envía la solicitud
- **THEN** el sistema devuelve `403 Forbidden` antes de ejecutar cualquier lógica de negocio

#### Scenario: Sin autenticación
- **WHEN** la solicitud no incluye header `Authorization: Bearer <token>`
- **THEN** el sistema devuelve `401 Unauthorized`

### Requirement: Snapshot de precios en líneas de pedido
El sistema SHALL capturar el precio y nombre del producto al momento de la creación del pedido. Los campos `nombre_snapshot` y `precio_snapshot` de `DetallePedido` NO SHALL ser actualizados si el precio del producto cambia posteriormente.

#### Scenario: Snapshot correcto al crear
- **WHEN** se crea un pedido con un producto que tiene `precio_base = 1500.00` y `nombre = "Pizza Margherita"`
- **THEN** el `DetallePedido` resultante tiene `precio_snapshot = 1500.00` y `nombre_snapshot = "Pizza Margherita"` independientemente de cambios futuros al producto

#### Scenario: Subtotal calculado correctamente
- **WHEN** se crea una línea con `precio_snapshot = 1500.00` y `cantidad = 3`
- **THEN** `subtotal = 4500.00` y el `total` del pedido incluye este subtotal

### Requirement: Descuento atómico de stock
El sistema SHALL decrementar `Producto.stock_cantidad` en la cantidad solicitada para cada línea de pedido dentro de la misma transacción de creación. Si la transacción falla, el stock SHALL retornar a su valor original.

#### Scenario: Stock decrementado tras creación exitosa
- **WHEN** se crea un pedido con 2 unidades del producto P1 que tenía stock = 10
- **THEN** el producto P1 tiene `stock_cantidad = 8` después del commit

#### Scenario: Stock no decrementado si la operación falla
- **WHEN** la creación falla por stock insuficiente en cualquier producto
- **THEN** ningún `stock_cantidad` es modificado (rollback total)

#### Scenario: Concurrencia — dos pedidos simultáneos del mismo producto con stock = 1
- **WHEN** dos requests concurrentes intentan comprar el mismo producto con stock = 1
- **THEN** solo uno tiene éxito (201) y el otro recibe 422 `PEDIDO_STOCK_INSUFICIENTE`; el stock final es 0 y no negativo

### Requirement: Registro de historial de estado inicial
El sistema SHALL crear una entrada en `HistorialEstadoPedido` con `estado_desde = NULL` y `estado_hasta = "PENDIENTE"` al momento de crear el pedido.

#### Scenario: Historial creado en creación de pedido
- **WHEN** se crea un pedido exitosamente
- **THEN** existe exactamente una entrada en `HistorialEstadoPedido` con `pedido_id` del nuevo pedido, `estado_desde = NULL` y `estado_hasta = "PENDIENTE"`
