## MODIFIED Requirements

### Requirement: Consultar pedido por ID con historial

El sistema SHALL exponer `GET /api/v1/pedidos/{id}` que devuelve el `PedidoDetail` completo incluyendo su `historial_estados` ordenado por `created_at` ascendente e información de pago asociada.

`PedidoDetail` SHALL incluir:
- `id`, `estado_actual`, `subtotal`, `descuento`, `costo_envio`, `total`, `created_at`
- `detalles: list[DetallePedidoRead]` con snapshots de productos
- `historial_estados: list[HistorialEstadoRead]`
- `pago`: información resumida del pago (`id`, `estado_pago`, `metodo_pago`, `monto`)

#### Scenario: Pedido existe con detalle completo
- **WHEN** se envía `GET /api/v1/pedidos/1`
- **THEN** el sistema responde `200 OK` con un `PedidoDetail` que incluye `detalles`, `historial_estados`, y `pago`

#### Scenario: Pedido no existe
- **WHEN** se envía `GET /api/v1/pedidos/999`
- **THEN** el sistema responde `404 Not Found` con error `PEDIDO_NOT_FOUND`

#### Scenario: Pedido de otro usuario (CLIENTE)
- **WHEN** un usuario CLIENTE solicita un pedido que pertenece a otro usuario
- **THEN** el sistema responde `403 Forbidden` con error `PEDIDO_NO_AUTORIZADO`

#### Scenario: Pedido sin pago asociado devuelve pago null
- **WHEN** se consulta un pedido que no tiene ningún pago registrado
- **THEN** el campo `pago` en `PedidoDetail` es `null`

### Requirement: Listar pedidos del usuario con paginación page/size

El sistema SHALL exponer `GET /api/v1/pedidos/` que lista los pedidos del usuario autenticado. Para roles ADMIN y GESTOR_PEDIDOS, SHALL listar todos los pedidos. SHALL soportar filtros opcionales por `estado`, `fecha_desde`, `fecha_hasta` y paginación (`page`, `size`).

La respuesta SHALL usar el formato:
```json
{
  "items": [PedidoRead, ...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

`PedidoRead` (compacto para listados) SHALL incluir solo: `id`, `estado_actual`, `subtotal`, `descuento`, `costo_envio`, `total`, `created_at`.

Si `page` o `size` no se proporcionan, los valores por defecto SHALL ser `page=1` y `size=20`.

El valor máximo de `size` SHALL ser 100.

#### Scenario: CLIENTE lista sus pedidos con page/size
- **WHEN** un usuario CLIENTE envía `GET /api/v1/pedidos/?page=1&size=20`
- **THEN** el sistema responde `200 OK` con `{ items: [...], total: N, page: 1, size: 20, pages: P }` conteniendo solo los pedidos donde `usuario_id` coincide

#### Scenario: ADMIN lista todos los pedidos
- **WHEN** un usuario ADMIN envía `GET /api/v1/pedidos/`
- **THEN** el sistema responde `200 OK` con todos los pedidos del sistema

#### Scenario: Filtrar por estado con paginación
- **WHEN** se envía `GET /api/v1/pedidos/?estado=PENDIENTE&page=1&size=20`
- **THEN** el sistema responde solo los pedidos con `estado_actual = "PENDIENTE"`, paginados

#### Scenario: Filtrar por rango de fechas
- **WHEN** se envía `GET /api/v1/pedidos/?fecha_desde=2026-01-01&fecha_hasta=2026-01-31`
- **THEN** el sistema responde solo los pedidos con `created_at` dentro del rango, paginados

#### Scenario: Página más allá del total devuelve items vacío
- **WHEN** se envía `GET /api/v1/pedidos/?page=999&size=20`
- **THEN** el sistema responde `200 OK` con `items: []` y `pages` calculado correctamente

#### Scenario: Size mayor a 100 se limita a 100
- **WHEN** se envía `GET /api/v1/pedidos/?size=500`
- **THEN** el sistema responde con `size=100` (máximo permitido)

#### Scenario: page=0 se trata como page=1
- **WHEN** se envía `GET /api/v1/pedidos/?page=0`
- **THEN** el sistema responde como si fuera `page=1`

### Requirement: Schema PedidoRead (compacto)

El sistema SHALL definir un schema Pydantic `PedidoRead` con campos: `id: int`, `estado_actual: str`, `subtotal: Decimal`, `descuento: Decimal`, `costo_envio: Decimal`, `total: Decimal`, `created_at: datetime`. Este schema NO SHALL incluir `detalles`, `historial_estados`, ni datos de `pago`.

#### Scenario: PedidoRead usado en listados
- **WHEN** se llama a `GET /api/v1/pedidos/`
- **THEN** cada item en `items` es un `PedidoRead` (compacto, sin detalles ni historial)

### Requirement: Schema PedidoDetail (completo)

El sistema SHALL definir un schema Pydantic `PedidoDetail` que extiende `PedidoRead` agregando: `detalles: list[DetallePedidoRead]`, `historial_estados: list[HistorialEstadoRead]`, y `pago: Optional[PagoResumen]`.

`PagoResumen` SHALL incluir: `id`, `estado_pago` (aprobado/rechazado/pendiente), `metodo_pago` (tarjeta/rapipago/pago_facil), `monto`.

#### Scenario: PedidoDetail usado en detalle
- **WHEN** se llama a `GET /api/v1/pedidos/{id}`
- **THEN** la respuesta es un `PedidoDetail` con todos los campos completos

### Requirement: Migración gradual de paginación

El sistema SHALL aceptar temporalmente los parámetros `limit` y `offset` además de `page` y `size` para mantener backward compatibility. Si se usan `limit/offset`, el sistema SHALL convertirlos internamente. Los parámetros `limit/offset` SHALL ser considerados deprecados.

#### Scenario: limit/offset sigue funcionando
- **WHEN** se envía `GET /api/v1/pedidos/?limit=20&offset=0`
- **THEN** el sistema responde `200 OK` con el formato `page/size` (convierte internamente)
