## 1. Modelo y migración

- [x] 1.1 Verificar que las tablas `pedido` y `detallepedido` existen en la BD (correr `alembic current` y revisar heads)
- [x] 1.2 Modificar `Pedido.forma_pago_codigo` para que sea nullable (`Optional[str]`) en `backend/pedidos/model.py`
- [x] 1.3 Generar migración Alembic para hacer `forma_pago_codigo` nullable: `alembic revision --autogenerate -m "make_forma_pago_nullable_pedido"`
- [x] 1.4 Revisar la migración generada y agregar `CHECK (stock_cantidad >= 0)` en tabla `producto` si no existe
- [x] 1.5 Aplicar la migración: `alembic upgrade head`
- [x] 1.6 Verificar que el seed de `estadopedido` incluye el registro `PENDIENTE` (si no existe, agregar en seed)

## 2. Schemas Pydantic

- [x] 2.1 Refactorizar `PedidoCreate` en `backend/pedidos/schemas.py`: eliminar `usuario_id` y `forma_pago_codigo` del body; mantener solo `direccion_id: int` y `detalles: list[DetallePedidoCreate]`
- [x] 2.2 Agregar validador en `PedidoCreate` que rechace `detalles = []` con mensaje `PEDIDO_CARRITO_VACIO`
- [x] 2.3 Actualizar `PedidoRead` para reflejar `forma_pago_codigo: Optional[str]` y `notas: Optional[str]`
- [x] 2.4 Crear schema `PedidoCreatedResponse` si se desea separar la respuesta de creación del modelo de lectura general (opcional — puede reutilizarse `PedidoRead`)

## 3. Repositorios

- [x] 3.1 Implementar `PedidoRepository(BaseRepository[Pedido])` en `backend/pedidos/repository.py` con método `get_by_id_active(id: int) -> Optional[Pedido]`
- [x] 3.2 Implementar `DetallePedidoRepository(BaseRepository[DetallePedido])` en `backend/pedidos/repository.py`
- [x] 3.3 Agregar método `get_by_id_active_with_lock(id: int) -> Optional[Producto]` en `backend/productos/repository.py` usando `select(...).with_for_update()` para descuento seguro de stock
- [x] 3.4 Verificar que `DireccionEntregaRepository` en `backend/direcciones/repository.py` tiene método `get_by_id_active(id: int) -> Optional[DireccionEntrega]`

## 4. Registro de repositorios en UoW

- [x] 4.1 Importar `PedidoRepository`, `DetallePedidoRepository` desde `backend.pedidos.repository` en `backend/core/dependencies.py`
- [x] 4.2 Importar `ProductoRepository` desde `backend.productos.repository` en `backend/core/dependencies.py` (si no está ya importado)
- [x] 4.3 Importar `DireccionEntregaRepository` desde `backend.direcciones.repository` en `backend/core/dependencies.py`
- [x] 4.4 Registrar los cuatro nuevos repos en `_register_repos()`: `pedidos`, `detalles_pedido`, `productos`, `direcciones`

## 5. Service

- [x] 5.1 Implementar función `crear_pedido(uow: UnitOfWork, data: PedidoCreate, current_user: Usuario) -> Pedido` en `backend/pedidos/service.py`
- [x] 5.2 En `crear_pedido`: validar que `data.detalles` no está vacío → `BadRequestException("PEDIDO_CARRITO_VACIO")`
- [x] 5.3 En `crear_pedido`: cargar `DireccionEntrega` por `data.direccion_id` → `NotFoundException("PEDIDO_DIRECCION_NOT_FOUND")` si no existe
- [x] 5.4 En `crear_pedido`: verificar `direccion.usuario_id == current_user.id` → `ForbiddenException("PEDIDO_DIRECCION_NO_AUTORIZADA")`
- [x] 5.5 En `crear_pedido`: para cada detalle, cargar `Producto` con `get_by_id_active_with_lock` → `ValidationException("PEDIDO_PRODUCTO_NO_DISPONIBLE: producto_id={id}")` si no existe o `disponible=False`
- [x] 5.6 En `crear_pedido`: verificar `producto.stock_cantidad >= detalle.cantidad` → `ValidationException("PEDIDO_STOCK_INSUFICIENTE: producto_id={id}, disponible={stock}")` si falla
- [x] 5.7 En `crear_pedido`: crear instancia `Pedido` con `usuario_id=current_user.id`, `direccion_id=data.direccion_id`, `estado_actual="PENDIENTE"`, `total=Decimal("0")`, `costo_envio=Decimal("0")`, `forma_pago_codigo=None`
- [x] 5.8 En `crear_pedido`: llamar `uow.repos.pedidos.add(pedido)` para obtener `pedido.id`
- [x] 5.9 En `crear_pedido`: para cada detalle, crear `DetallePedido` con snapshot y calcular `subtotal = precio_snapshot * cantidad`; agregar vía `uow.repos.detalles_pedido.add(detalle)`
- [x] 5.10 En `crear_pedido`: descontar stock de cada producto (`producto.stock_cantidad -= detalle.cantidad`) y llamar `uow.repos.productos.update(producto)`
- [x] 5.11 En `crear_pedido`: calcular `pedido.total = sum(d.subtotal for d in detalles)` y actualizar el pedido
- [x] 5.12 En `crear_pedido`: crear entrada en `HistorialEstadoPedido` con `pedido_id=pedido.id`, `estado_desde=None`, `estado_hasta="PENDIENTE"`
- [x] 5.13 Retornar el `pedido` (con detalles populados tras flush)

## 6. Router

- [x] 6.1 Implementar `POST /` en `backend/pedidos/router.py` con `response_model=PedidoRead`, `status_code=201`
- [x] 6.2 Aplicar dependencia `require_role("CLIENTE")` para restringir acceso
- [x] 6.3 Inyectar `uow: UnitOfWork = Depends(get_uow)` y `current_user: Usuario = Depends(require_role("CLIENTE"))`
- [x] 6.4 Llamar `service.crear_pedido(uow, body, current_user)`, luego `uow.commit()`, retornar resultado con status 201
- [x] 6.5 Incluir el router en `backend/main.py` con prefix `/api/v1/pedidos` y tag `pedidos`

## 7. Verificación y pruebas manuales

- [x] 7.1 Verificar importaciones circulares con `python -c "from backend.pedidos import router"`
- [x] 7.2 Levantar el servidor y probar `POST /api/v1/pedidos` con usuario CLIENTE, dirección válida, productos con stock
- [x] 7.3 Probar caso de stock insuficiente y verificar que el stock NO se decrementó
- [x] 7.4 Probar con dirección de otro usuario y verificar 403
- [x] 7.5 Probar con usuario ADMIN y verificar 403
- [x] 7.6 Probar con carrito vacío y verificar 400
- [x] 7.7 Verificar en BD que `HistorialEstadoPedido` tiene una entrada con `estado_desde=NULL, estado_hasta=PENDIENTE`
