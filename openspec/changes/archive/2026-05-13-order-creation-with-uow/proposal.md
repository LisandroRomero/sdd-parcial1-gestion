## Why

El sistema tiene productos con stock, direcciones de entrega y usuarios autenticados con roles, pero no existe ningún flujo que permita a un cliente crear un pedido a partir de esos datos. Sin esta funcionalidad, el e-commerce no puede facturar ni procesar ninguna compra. Este epic implementa el núcleo de la transacción de compra: el cliente envía su carrito, se valida stock y titularidad de dirección, se captura el snapshot de precios, y se descuenta stock — todo de forma atómica vía UoW.

## What Changes

- **Nuevo endpoint** `POST /api/v1/pedidos` — crea un pedido con todas sus líneas en una única transacción atómica.
- **Snapshot de precios**: cada `DetallePedido` almacena `nombre_snapshot` y `precio_snapshot` copiados del `Producto` al momento de la compra (no FK al precio actual).
- **Validación de stock por línea**: si cualquier producto tiene `stock_cantidad < cantidad_solicitada`, la operación completa hace rollback.
- **Descuento atómico de stock**: `Producto.stock_cantidad -= cantidad` para cada línea dentro de la misma transacción.
- **Validación de ownership de dirección**: la `DireccionEntrega.usuario_id` debe coincidir con el usuario autenticado; de lo contrario, 403.
- **Estado inicial**: todo pedido creado comienza con `estado_actual = "PENDIENTE"`.
- **Restricción de rol**: solo usuarios con rol `CLIENTE` pueden acceder al endpoint; `ADMIN`, `GESTOR_STOCK`, `GESTOR_PEDIDOS` reciben 403.
- **PedidoRepository** y **DetallePedidoRepository** — nuevos repositorios que heredan `BaseRepository[T]`.
- **PedidoService** — orquesta las validaciones y la creación atómica.
- **Registro de repos** en `core/dependencies.py` (`pedidos`, `detalles_pedido`, `productos`, `direcciones`).
- **Alembic migration** — creación de tablas `pedido` y `detallepedido` (si no existen aún).
- **Schemas Pydantic**: `PedidoCreate` actualizado para aceptar solo `direccion_id` + `detalles` (sin `usuario_id` ni `forma_pago_codigo` — el usuario viene del JWT).

## Capabilities

### New Capabilities

- `order-creation`: Creación atómica de pedidos con snapshot de precios, validación de stock y descuento de inventario en una única transacción UoW.

### Modified Capabilities

- `uow-repository`: El `get_uow` de `core/dependencies.py` debe registrar los nuevos repositorios (`pedidos`, `detalles_pedido`, `productos`, `direcciones`) para que estén disponibles en la transacción.

## Impact

- **backend/pedidos/**: `model.py` (ya existe con estructura parcial), `schemas.py` (refactor para alinearse al spec), `repository.py` (nuevo: `PedidoRepository`, `DetallePedidoRepository`), `service.py` (nuevo: lógica de creación), `router.py` (nuevo: endpoint `POST /api/v1/pedidos`)
- **backend/core/dependencies.py**: registro de repos `pedidos`, `detalles_pedido`, `productos`, `direcciones` en `_register_repos()`
- **backend/productos/repository.py**: potencial agregado de método `get_by_id_active_with_lock()` o uso de `select ... FOR UPDATE` para descuento de stock seguro
- **alembic/versions/**: nueva migración para tablas `pedido` y `detallepedido`
- **Dependencias**: ninguna nueva librería; usa `Decimal` de stdlib y `require_role` ya implementado
- **Testing**: endpoints de pedidos requieren usuario con rol `CLIENTE` + direcciones + productos con stock
