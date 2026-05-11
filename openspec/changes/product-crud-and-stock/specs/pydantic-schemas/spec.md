## MODIFIED Requirements

### Requirement: Schemas Pydantic para Producto
El sistema SHALL definir los siguientes schemas en `backend/productos/schemas.py`:
- `ProductoCreate`: campos base + `categoria_ids: list[int] = []` para asociación de categorías al crear. Valida `precio_base > 0` y `stock_cantidad >= 0`.
- `ProductoUpdate`: todos los campos opcionales + `categoria_ids: Optional[list[int]] = None`. Si `categoria_ids` es `None`, las categorías existentes se preservan.
- `ProductoRead`: campos de lectura incluyendo `id`, `codigo_sku`, `nombre`, `descripcion`, `precio_base`, `stock_cantidad`, `disponible`, `imagen_url`, `created_at`, `updated_at`.
- `StockUpdate`: `{ stock_cantidad: int }` con validación `>= 0`. Nuevo schema.
- `DisponibilidadUpdate`: `{ disponible: bool }`. Nuevo schema.
- `ProductoPaginado`: `{ items: list[ProductoRead], total: int, page: int, size: int, pages: int }`. Para uso futuro en change 2.5.

#### Scenario: Precio base con precisión decimal
- **WHEN** se crea un Producto con precio_base
- **THEN** SHALL aceptar hasta 2 decimales y validar que sea > 0

#### Scenario: Stock no negativo
- **WHEN** se crea o actualiza stock_cantidad
- **THEN** SHALL validar que sea >= 0

#### Scenario: StockUpdate rechaza negativos
- **WHEN** se envía `StockUpdate` con `stock_cantidad < 0`
- **THEN** retorna `422 Unprocessable Entity`

#### Scenario: categoria_ids ausente en Update preserva categorías
- **WHEN** `ProductoUpdate` no incluye `categoria_ids` (campo es None)
- **THEN** el service interpreta esto como "no modificar categorías"
