### Requirement: Listar productos públicamente con paginación y filtros
El sistema SHALL exponer `GET /api/v1/productos` sin autenticación, retornando un listado paginado de productos activos (`deleted_at IS NULL`) con `disponible = True` por defecto. El endpoint SHALL soportar los query params: `page` (entero ≥ 1, default 1), `size` (entero 1-100, default 20), `categoria_id` (entero, opcional), `disponible` (bool, opcional — por defecto solo visibles), `precio_min` (decimal, opcional), `precio_max` (decimal, opcional), `busqueda` (string, opcional — ILIKE en `nombre` y `descripcion`), `tiene_alergenos` (bool, opcional). La respuesta SHALL tener forma `ProductoPaginado` con `items: list[ProductoRead]`, `total`, `page`, `size`, `pages`.

#### Scenario: Listado sin filtros retorna productos disponibles paginados
- **WHEN** un cliente anónimo hace `GET /api/v1/productos` sin query params
- **THEN** el sistema retorna `200 OK` con `ProductoPaginado` donde todos los `items` tienen `disponible = True` y `deleted_at IS NULL`, `page = 1`, `size = 20`

#### Scenario: Filtro por categoria_id
- **WHEN** se hace `GET /api/v1/productos?categoria_id=5`
- **THEN** solo se incluyen productos que tienen una fila en `producto_categorias` con `categoria_id = 5`

#### Scenario: Filtro por rango de precio
- **WHEN** se hace `GET /api/v1/productos?precio_min=100&precio_max=500`
- **THEN** solo se incluyen productos con `precio_base >= 100` y `precio_base <= 500`

#### Scenario: Filtro precio_min mayor que precio_max
- **WHEN** se hace `GET /api/v1/productos?precio_min=500&precio_max=100`
- **THEN** retorna `422 Unprocessable Entity` con detalle de validación

#### Scenario: Búsqueda por texto
- **WHEN** se hace `GET /api/v1/productos?busqueda=pizza`
- **THEN** solo se incluyen productos donde `nombre ILIKE '%pizza%'` OR `descripcion ILIKE '%pizza%'`

#### Scenario: Filtro tiene_alergenos=true
- **WHEN** se hace `GET /api/v1/productos?tiene_alergenos=true`
- **THEN** solo se incluyen productos que tienen al menos un ingrediente activo (`ingrediente.deleted_at IS NULL`) con `es_alergeno = True`

#### Scenario: Filtro tiene_alergenos=false
- **WHEN** se hace `GET /api/v1/productos?tiene_alergenos=false`
- **THEN** solo se incluyen productos que NO tienen ningún ingrediente activo con `es_alergeno = True`

#### Scenario: Paginación correcta con múltiples páginas
- **WHEN** existen 45 productos disponibles y se hace `GET /api/v1/productos?page=2&size=20`
- **THEN** retorna `items` con los productos 21-40, `total = 45`, `page = 2`, `size = 20`, `pages = 3`

#### Scenario: Página fuera de rango retorna lista vacía
- **WHEN** se hace `GET /api/v1/productos?page=999`
- **THEN** retorna `200 OK` con `items = []`, `total` correcto y `pages` correcto

#### Scenario: Productos soft-deleted no aparecen en el listado
- **WHEN** un producto tiene `deleted_at` poblado
- **THEN** ese producto NO aparece en el listado público bajo ningún filtro

### Requirement: Ver detalle público de un producto
El sistema SHALL exponer `GET /api/v1/productos/{id}` sin autenticación, retornando el detalle completo de un producto activo (`deleted_at IS NULL`) con sus categorías e ingredientes activos. La respuesta SHALL ser `ProductoDetalleRead` con todos los campos de `ProductoRead` más: `categorias: list[CategoriaRead]`, `ingredientes: list[ProductoIngredienteRead]`, `tiene_alergenos: bool` (derivado — `True` si algún ingrediente activo tiene `es_alergeno = True`).

#### Scenario: Detalle exitoso de producto activo
- **WHEN** se hace `GET /api/v1/productos/1` y el producto con id=1 existe con `deleted_at IS NULL`
- **THEN** retorna `200 OK` con `ProductoDetalleRead` incluyendo el producto, sus categorías activas y sus ingredientes activos

#### Scenario: El campo tiene_alergenos es True cuando hay ingredientes alérgenos
- **WHEN** el producto tiene al menos un ingrediente activo con `es_alergeno = True`
- **THEN** `tiene_alergenos = True` en la respuesta

#### Scenario: El campo tiene_alergenos es False cuando no hay ingredientes alérgenos
- **WHEN** el producto no tiene ingredientes activos con `es_alergeno = True`
- **THEN** `tiene_alergenos = False` en la respuesta

#### Scenario: Ingredientes soft-deleted no aparecen en el detalle
- **WHEN** un ingrediente asociado al producto fue soft-deleted
- **THEN** ese ingrediente NO aparece en `ingredientes` de la respuesta (JOIN filtra `ingrediente.deleted_at IS NULL`)

#### Scenario: Producto no encontrado
- **WHEN** el id no existe o el producto tiene `deleted_at` poblado
- **THEN** retorna `404 Not Found` con `code: PRODUCTO_NOT_FOUND`

#### Scenario: Detalle de producto sin ingredientes ni categorías
- **WHEN** el producto existe pero no tiene asociaciones en `producto_ingredientes` ni `producto_categorias`
- **THEN** retorna `200 OK` con `categorias = []`, `ingredientes = []`, `tiene_alergenos = False`

### Requirement: Schema ProductoDetalleRead
El sistema SHALL definir el schema `ProductoDetalleRead` en `backend/productos/schemas.py` extendiendo `ProductoRead` con los campos: `categorias: list[CategoriaRead]` (default `[]`), `ingredientes: list[ProductoIngredienteRead]` (default `[]`), `tiene_alergenos: bool` (default `False`). El schema SHALL ser capaz de construirse desde atributos ORM (`from_attributes = True`).

#### Scenario: Construcción válida de ProductoDetalleRead
- **WHEN** se construye `ProductoDetalleRead.model_validate(producto_orm_con_relaciones)`
- **THEN** el schema se construye correctamente con todos los campos poblados

### Requirement: Schema ProductoFiltros como dependency de query params
El sistema SHALL definir `ProductoFiltros` como `BaseModel` con todos los query params del endpoint de listado. El modelo SHALL validar que `precio_min <= precio_max` cuando ambos están presentes. El endpoint SHALL recibir los filtros mediante `Depends(ProductoFiltros)`.

#### Scenario: Validación de rango de precio en ProductoFiltros
- **WHEN** `precio_min > precio_max` en los query params
- **THEN** Pydantic lanza `ValidationError` y FastAPI retorna `422 Unprocessable Entity`

#### Scenario: Todos los filtros son opcionales
- **WHEN** se instancia `ProductoFiltros` sin ningún parámetro
- **THEN** todos los campos opcionales son `None` y `page=1`, `size=20`

### Requirement: Frontend — tipos ProductoFiltros y ProductoPaginado
El frontend SHALL definir los tipos `ProductoFiltros` y `ProductoPaginado` en `frontend/src/entities/producto/types.ts` para tipar las consultas al catálogo público.

`ProductoFiltros`:
- `page?: number` — página actual (default 1 en backend)
- `size?: number` — tamaño de página (default 20 en backend)
- `categoria_id?: number` — filtro por categoría
- `precio_min?: number` — precio mínimo
- `precio_max?: number` — precio máximo
- `busqueda?: string` — búsqueda por texto (nombre o descripción)
- `tiene_alergenos?: boolean` — filtrar por presencia de alérgenos

`ProductoPaginado`:
- `items: ProductoRead[]` — lista de productos
- `total: number` — total de resultados
- `page: number` — página actual
- `size: number` — tamaño de página
- `pages: number` — total de páginas

#### Scenario: ProductoFiltros es totalmente opcional
- **WHEN** se instancia `ProductoFiltros` sin ningún campo
- **THEN** todos los campos son `undefined` y el request al backend usa los defaults del servidor

#### Scenario: ProductoPaginado refleja la respuesta del backend
- **WHEN** el backend retorna `{ items: [...], total: 45, page: 2, size: 20, pages: 3 }`
- **THEN** `ProductoPaginado` mapea 1:1 sin conversión adicional
