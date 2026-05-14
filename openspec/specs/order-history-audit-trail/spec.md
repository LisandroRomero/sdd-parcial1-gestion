# Spec: order-history-audit-trail

### Requirement: Endpoint historial autorizado

El sistema SHALL exponer `GET /api/v1/pedidos/{id}/historial` que devuelve el audit trail completo del pedido ordenado por `created_at` ascendente. El endpoint SHALL validar autorización según el rol del usuario autenticado.

CLIENT users SHALL only see history of their own orders. ADMIN and GESTOR_PEDIDOS SHALL see history of any order.

#### Scenario: CLIENT ve historial de su propio pedido
- **WHEN** un usuario con rol `CLIENTE` envía `GET /api/v1/pedidos/{id}/historial` donde `id` pertenece a su propio `usuario_id`
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: CLIENT no ve historial de pedido ajeno
- **WHEN** un usuario con rol `CLIENTE` envía `GET /api/v1/pedidos/{id}/historial` donde `id` pertenece a otro usuario
- **THEN** el sistema responde `403 Forbidden` con error `PEDIDO_NO_AUTORIZADO`

#### Scenario: ADMIN ve historial de cualquier pedido
- **WHEN** un usuario con rol `ADMIN` envía `GET /api/v1/pedidos/{id}/historial` para cualquier pedido
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: GESTOR_PEDIDOS ve historial de cualquier pedido
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` envía `GET /api/v1/pedidos/{id}/historial` para cualquier pedido
- **THEN** el sistema responde `200 OK` con el array de entradas del historial

#### Scenario: Pedido inexistente devuelve 404
- **WHEN** se envía `GET /api/v1/pedidos/99999/historial`
- **THEN** el sistema responde `404 Not Found` con error `PEDIDO_NOT_FOUND`

### Requirement: Estructura de datos del historial

Cada entrada del historial SHALL incluir los campos: `estado_desde` (string o null), `estado_hasta` (string), `usuario_id` (integer o null), `motivo` (string o null), y `created_at` (datetime).

La primera entrada del historial SHALL tener `estado_desde = NULL` representando la creación del pedido (RN-02).

#### Scenario: Historial con múltiples transiciones
- **WHEN** se consulta el historial de un pedido con 3 cambios de estado
- **THEN** el sistema responde un array de 3 entradas ordenadas cronológicamente por `created_at` ASC

#### Scenario: Primera entrada con estado_desde NULL
- **WHEN** se consulta el historial de un pedido
- **THEN** la primera entrada (más antigua) tiene `estado_desde = NULL` y `estado_hasta = "PENDIENTE"`

#### Scenario: Transición manual registra usuario_id
- **WHEN** un usuario autenticado avanzó el estado del pedido
- **THEN** la entrada del historial tiene `usuario_id` del usuario que ejecutó la acción

#### Scenario: Transición del sistema registra usuario_id NULL
- **WHEN** el sistema cambió el estado automáticamente
- **THEN** la entrada del historial tiene `usuario_id = NULL`

#### Scenario: Cancelación registra motivo
- **WHEN** se cancela un pedido con motivo
- **THEN** la entrada del historial tiene `motivo` con el texto provisto

#### Scenario: Transición sin motivo registra NULL
- **WHEN** se avanza un pedido sin proporcionar motivo
- **THEN** la entrada del historial tiene `motivo = NULL`

### Requirement: Componente OrderTimeline (frontend)

El frontend SHALL tener un componente `OrderTimeline` ubicado en `entities/pedidos/ui/OrderTimeline/` que renderiza el historial de estados como una línea de tiempo vertical con indicadores de color por estado.

#### Scenario: Timeline muestra estados cronológicos
- **WHEN** se renderiza `OrderTimeline` con un array de `HistorialEstadoRead[]`
- **THEN** se muestran las entradas en orden cronológico ascendente con:
  - Círculo coloreado según el estado (usando `statusColors`)
  - Línea vertical conectando entradas consecutivas
  - Nombre del estado en español (usando `statusLabels`)
  - Texto de transición: "desde {estado_desde}" excepto en la primera entrada
  - Timestamp formateado con locale `es-AR`
  - `motivo` en texto secundario si está presente

#### Scenario: Timeline recibe historial por prop
- **WHEN** se usa `OrderTimeline` en `PedidoDetailPage`
- **THEN** recibe `historial` como prop de tipo `HistorialEstadoRead[]` desde `pedido.historial_estados`

#### Scenario: Timeline vacío no se renderiza
- **WHEN** el array de historial está vacío
- **THEN** el componente no renderiza nada (null/empty fragment)

### Requirement: Status colors y labels compartidos

El sistema frontend SHALL definir `statusColors` y `statusLabels` como constantes compartidas en `entities/pedidos/`, extraídas de las definiciones inline actuales en `PedidoDetailPage.tsx` y `CancelarPedidoModal.tsx`.

#### Scenario: statusColors define color por estado
- **WHEN** se consulta `statusColors["ENTREGADO"]`
- **THEN** devuelve un color verde (`#22c55e` o clase `text-green-500`)

#### Scenario: statusLabels define etiqueta en español
- **WHEN** se consulta `statusLabels["EN_PREP"]`
- **THEN** devuelve `"En preparación"` (o la etiqueta en español correspondiente)
