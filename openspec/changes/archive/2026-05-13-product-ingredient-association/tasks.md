## 1. Modelo y Migración

- [x] 1.1 Agregar `cantidad: Optional[float] = None` y `unidad: Optional[str] = Field(default=None, max_length=20)` al modelo `ProductoIngrediente` en `backend/ingredientes/model.py`
- [x] 1.2 Generar migración Alembic con `alembic revision --autogenerate -m "add_cantidad_unidad_to_producto_ingredientes"`
- [x] 1.3 Revisar el script de migración autogenerado en `alembic/versions/` — confirmar que solo agrega `ADD COLUMN cantidad FLOAT` y `ADD COLUMN unidad VARCHAR(20)` a `producto_ingredientes`
- [x] 1.4 Ejecutar `alembic upgrade head` y verificar que la BD refleja los nuevos campos

## 2. Schemas Pydantic

- [x] 2.1 Agregar `ProductoIngredienteCreate` en `backend/ingredientes/schemas.py` con campos: `ingrediente_id: int`, `cantidad: Optional[float] = None`, `unidad: Optional[str] = None`
- [x] 2.2 Agregar `ProductoIngredienteRead` en `backend/ingredientes/schemas.py` con campos: `ingrediente_id: int`, `nombre: str`, `es_alergeno: bool`, `cantidad: Optional[float]`, `unidad: Optional[str]`, `es_removible: bool` — con `model_config = ConfigDict(from_attributes=True)`
- [x] 2.3 Agregar `ProductoIngredienteListResponse` en `backend/ingredientes/schemas.py` con campos: `items: list[ProductoIngredienteRead]`, `total: int`

## 3. Repository

- [x] 3.1 Agregar método `agregar_a_producto(self, producto_id: int, ingrediente_id: int, cantidad: Optional[float], unidad: Optional[str]) -> ProductoIngrediente` en `backend/ingredientes/repository.py`
- [x] 3.2 Agregar método `existe_asociacion(self, producto_id: int, ingrediente_id: int) -> bool` en `backend/ingredientes/repository.py`
- [x] 3.3 Agregar método `listar_por_producto(self, producto_id: int) -> list[tuple[ProductoIngrediente, Ingrediente]]` en `backend/ingredientes/repository.py` — JOIN con `Ingrediente` filtrando `Ingrediente.deleted_at IS NULL`
- [x] 3.4 Agregar método `remover_de_producto(self, producto_id: int, ingrediente_id: int) -> bool` en `backend/ingredientes/repository.py` — retorna `False` si no existe la asociación

## 4. Service

- [x] 4.1 Agregar función `asociar_ingrediente(uow: UnitOfWork, producto_id: int, data: ProductoIngredienteCreate) -> ProductoIngrediente` en `backend/ingredientes/service.py` — valida producto activo (404), ingrediente activo (404), no duplicado (409), delega a repo
- [x] 4.2 Agregar función `listar_ingredientes_producto(uow: UnitOfWork, producto_id: int) -> ProductoIngredienteListResponse` en `backend/ingredientes/service.py` — valida producto activo (404), construye response con JOIN de ingredientes activos
- [x] 4.3 Agregar función `desasociar_ingrediente(uow: UnitOfWork, producto_id: int, ingrediente_id: int) -> None` en `backend/ingredientes/service.py` — valida producto activo (404), valida que la asociación existe (404 con `PRODUCTO_INGREDIENTE_NOT_FOUND`), delega remoción al repo

## 5. Router

- [x] 5.1 Extender `_get_uow` en `backend/productos/router.py` para registrar también `IngredienteRepository`: `uow.repos.register("ingredientes", lambda s: IngredienteRepository(s))` — importar `IngredienteRepository` desde `backend.ingredientes.repository`
- [x] 5.2 Agregar endpoint `POST /{id}/ingredientes` en `backend/productos/router.py` con `response_model=ProductoIngredienteRead`, `status_code=201`, `require_role("ADMIN", "STOCK")` — delega a `ingrediente_service.asociar_ingrediente`
- [x] 5.3 Agregar endpoint `GET /{id}/ingredientes` en `backend/productos/router.py` con `response_model=ProductoIngredienteListResponse`, `status_code=200`, sin autenticación — delega a `ingrediente_service.listar_ingredientes_producto`
- [x] 5.4 Agregar endpoint `DELETE /{id}/ingredientes/{ingrediente_id}` en `backend/productos/router.py` con `response_model=None`, `status_code=204`, `require_role("ADMIN", "STOCK")` — delega a `ingrediente_service.desasociar_ingrediente`

## 6. Verificación

- [x] 6.1 Verificar con `GET /api/v1/productos/{id}/ingredientes` que retorna 200 con lista vacía para producto sin ingredientes
- [x] 6.2 Verificar que `POST /api/v1/productos/{id}/ingredientes` retorna 201 con el payload correcto
- [x] 6.3 Verificar que un segundo POST con el mismo `ingrediente_id` retorna 409 con `code: PRODUCTO_INGREDIENTE_DUPLICADO`
- [x] 6.4 Verificar que `DELETE /api/v1/productos/{id}/ingredientes/{ingrediente_id}` retorna 204 y el ingrediente ya no aparece en el GET
- [x] 6.5 Verificar que tras soft-delete de un ingrediente, el GET de ingredientes del producto ya no lo retorna
- [x] 6.6 Verificar que usuarios sin rol ADMIN/STOCK reciben 403 en POST y DELETE
