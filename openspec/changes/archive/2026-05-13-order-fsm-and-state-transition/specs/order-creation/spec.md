## MODIFIED Requirements

### Requirement: Cliente puede crear un pedido

El sistema SHALL permitir a un usuario autenticado con rol CLIENTE crear un pedido a partir de una lista de productos, una forma de pago, y una dirección de entrega de su propiedad. La operación SHALL ser atómica: o todos los recursos se persisten correctamente o ninguno se persiste.

#### Scenario: Creación exitosa con stock suficiente
- **WHEN** el cliente autenticado envía `POST /api/v1/pedidos` con `direccion_id` válida (de su propiedad), `forma_pago_codigo` válido, y al menos un `DetallePedidoCreate` con `producto_id` válido, `cantidad >= 1`, y stock suficiente
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

#### Scenario: Forma de pago inválida
- **WHEN** el cliente envía un `forma_pago_codigo` que no existe en la tabla `FormaPago`
- **THEN** el sistema devuelve `422 Unprocessable Entity` con error `PEDIDO_FORMA_PAGO_INVALIDA`

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

### ADDED Requirements

### Requirement: Frontend entity para AvanzarEstadoRequest

El frontend SHALL definir el tipo `AvanzarEstadoRequest` en `frontend/src/entities/pedidos/types.ts` con `nuevo_estado: string` y `motivo?: string`.

### Requirement: Frontend API functions para ciclo de vida

El frontend SHALL implementar funciones en `frontend/src/entities/pedidos/api.ts`:

- `avanzarEstado(pedidoId: number, data: AvanzarEstadoRequest): Promise<PedidoRead>` — `PATCH /api/v1/pedidos/{id}/estado`
- `cancelarPedido(pedidoId: number, motivo: string): Promise<PedidoRead>` — `DELETE /api/v1/pedidos/{id}?motivo=...`
- `getPedido(pedidoId: number): Promise<PedidoRead>` — `GET /api/v1/pedidos/{id}`
- `listarPedidos(filtros?: { estado?: string, limit?: number, offset?: number }): Promise<PedidoRead[]>` — `GET /api/v1/pedidos/`
- `getHistorialPedido(pedidoId: number): Promise<HistorialEstadoRead[]>` — `GET /api/v1/pedidos/{id}/historial`

### Requirement: Frontend entity PedidoRead incluye historial

El frontend SHALL actualizar el tipo `PedidoRead` para incluir `historial_estados: HistorialEstadoRead[]`.

Además SHALL definir el tipo `HistorialEstadoRead`:

```typescript
interface HistorialEstadoRead {
  id: number
  estado_desde: string | null
  estado_hasta: string
  usuario_id: number | null
  motivo: string | null
  created_at: string
}
```
