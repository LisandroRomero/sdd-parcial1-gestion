## ADDED Requirements

### Requirement: Frontend entity para pedidos

El frontend SHALL definir tipos `PedidoCreate` y `PedidoRead` en `frontend/src/entities/pedidos/types.ts`.

`PedidoCreate` SHALL tener:
- `detalles: DetallePedidoCreate[]` — cada uno con `producto_id: number` y `cantidad: number`
- `direccion_id: number`

`PedidoRead` SHALL incluir al menos:
- `id: number`
- `estado_actual: string`
- `total: number`
- `direccion: { calle: string, numero: string, ciudad: string }`
- `detalles: { nombre_snapshot: string, cantidad: number, precio_snapshot: number, subtotal: number }[]`
- `created_at: string`

#### Scenario: Tipos pedidos definidos correctamente

- **WHEN** el frontend importa `PedidoCreate` y `PedidoRead`
- **THEN** ambos tipos SHALL existir y ser usables en las llamadas API

---

### Requirement: Frontend API para crear pedido

El frontend SHALL implementar una función `createPedido` en `frontend/src/entities/pedidos/api.ts` que realice `POST /api/v1/pedidos` usando el cliente Axios con interceptor JWT.

La función SHALL aceptar `data: PedidoCreate` y retornar una promesa de tipo `PedidoRead`.

#### Scenario: createPedido exitoso

- **WHEN** se llama `createPedido({ detalles: [{ producto_id: 1, cantidad: 2 }], direccion_id: 5 })`
- **AND** el backend responde con `201` y un `PedidoRead`
- **THEN** la función retorna el `PedidoRead` recibido

#### Scenario: createPedido con error

- **WHEN** el backend responde con error 422 o 400
- **THEN** la función rechaza la promesa con el error del backend
