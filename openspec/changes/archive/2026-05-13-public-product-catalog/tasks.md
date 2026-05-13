## 1. Schemas

- [x] 1.1 Agregar `ProductoFiltros(BaseModel)` en `backend/productos/schemas.py` con campos: `page: int = Field(default=1, ge=1)`, `size: int = Field(default=20, ge=1, le=100)`, `categoria_id: Optional[int] = None`, `disponible: Optional[bool] = None`, `precio_min: Optional[Decimal] = None`, `precio_max: Optional[Decimal] = None`, `busqueda: Optional[str] = None`, `tiene_alergenos: Optional[bool] = None`
- [x] 1.2 Agregar `model_validator(mode="after")` en `ProductoFiltros` que lance `ValueError` si `precio_min` y `precio_max` están ambos presentes y `precio_min > precio_max`
- [x] 1.3 Agregar `ProductoDetalleRead(ProductoRead)` en `backend/productos/schemas.py` con campos: `categorias: list[CategoriaRead] = []`, `ingredientes: list[ProductoIngredienteRead] = []`, `tiene_alergenos: bool = False` — importar `CategoriaRead` desde `backend.categorias.schemas` e `ProductoIngredienteRead` desde `backend.ingredientes.schemas`

## 2. Repository

- [x] 2.1 Agregar método `list_public(filtros: ProductoFiltros) -> tuple[list[Producto], int]` en `ProductoRepository` — query base con `deleted_at IS NULL` y `disponible = True` por defecto (si `filtros.disponible is None`); aplicar filtros opcionales en orden: `categoria_id` (JOIN a `producto_categorias`), `precio_min`, `precio_max`, `busqueda` (ILIKE en nombre y descripcion con `or_()`), `tiene_alergenos` (EXISTS subquery a `producto_ingredientes` + `ingredientes`); retornar `(items_paginados, total_count)`
- [x] 2.2 Agregar método `get_detalle_public(id: int) -> Optional[tuple[Producto, list[ProductoCategoria], list]]` en `ProductoRepository` — retornar el producto activo con sus categorías activas y sus ingredientes activos cargados explícitamente mediante queries separadas en la misma sesión

## 3. Service

- [x] 3.1 Agregar función `listar_publico(uow: UnitOfWork, filtros: ProductoFiltros) -> ProductoPaginado` en `backend/productos/service.py` — delegar a `uow.repos.get("productos").list_public(filtros)`, construir `ProductoPaginado` con `pages = ceil(total / size)`
- [x] 3.2 Agregar función `obtener_detalle_publico(uow: UnitOfWork, id: int) -> ProductoDetalleRead` en `backend/productos/service.py` — delegar a `uow.repos.get("productos").get_detalle_public(id)`, lanzar `HTTPException(404, code="PRODUCTO_NOT_FOUND")` si el producto no existe o tiene `deleted_at`, construir `ProductoDetalleRead` con `tiene_alergenos = any(i.es_alergeno for i in ingredientes)`

## 4. Router

- [x] 4.1 Agregar endpoint `GET /` en `backend/productos/router.py` **antes** de los endpoints protegidos existentes — sin dependency de autenticación, `response_model=ProductoPaginado`, `status_code=200`, recibir filtros con `Depends(ProductoFiltros)`, delegar a `producto_service.listar_publico(uow, filtros)`
- [x] 4.2 Agregar endpoint `GET /{id}` en `backend/productos/router.py` **antes** de los endpoints protegidos existentes — sin dependency de autenticación, `response_model=ProductoDetalleRead`, `status_code=200`, delegar a `producto_service.obtener_detalle_publico(uow, id)`

## 5. Verificación

- [x] 5.1 `GET /api/v1/productos` sin query params retorna `200` con lista de productos disponibles paginados (solo `disponible=True`, `deleted_at IS NULL`)
- [x] 5.2 `GET /api/v1/productos?categoria_id=1` retorna solo productos de esa categoría
- [x] 5.3 `GET /api/v1/productos?precio_min=100&precio_max=500` retorna solo productos en ese rango
- [x] 5.4 `GET /api/v1/productos?precio_min=500&precio_max=100` retorna `422`
- [x] 5.5 `GET /api/v1/productos?busqueda=pizza` retorna productos cuyo nombre o descripción contiene "pizza" (case-insensitive)
- [x] 5.6 `GET /api/v1/productos?tiene_alergenos=true` retorna solo productos con al menos un ingrediente alérgeno activo
- [x] 5.7 `GET /api/v1/productos?tiene_alergenos=false` retorna solo productos sin ingredientes alérgenos activos
- [x] 5.8 `GET /api/v1/productos/{id}` de un producto activo retorna `200` con `categorias`, `ingredientes` y `tiene_alergenos` correctos
- [x] 5.9 `GET /api/v1/productos/{id}` de un producto con `deleted_at` poblado retorna `404` con `code: PRODUCTO_NOT_FOUND`
- [x] 5.10 Los endpoints existentes `POST /api/v1/productos`, `PUT /api/v1/productos/{id}`, `DELETE /api/v1/productos/{id}` siguen funcionando y requiriendo ADMIN
