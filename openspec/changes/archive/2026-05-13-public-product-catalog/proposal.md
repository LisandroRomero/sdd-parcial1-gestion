## Why

El catálogo de productos no tiene endpoints públicos: actualmente todos los endpoints de `GET /api/v1/productos` requieren autenticación y rol de staff (ADMIN/STOCK). Los clientes sin cuenta —y los clientes autenticados— no pueden navegar el catálogo ni ver el detalle de un producto antes de hacer un pedido, bloqueando completamente el flujo de compra. Esta brecha cubre US-018, US-019 y US-023 del backlog.

## What Changes

- **Nuevo endpoint público** `GET /api/v1/productos` — listado paginado sin autenticación con soporte para filtros por categoría, disponibilidad, rango de precio, búsqueda de texto y presencia de alérgenos.
- **Nuevo endpoint público** `GET /api/v1/productos/{id}` — detalle completo de un producto que incluye sus categorías e ingredientes (con flag `es_alergeno`).
- **Nuevo schema** `ProductoDetalleRead` — extiende `ProductoRead` con listas de `CategoriaRead` e `ProductoIngredienteRead`, más el campo derivado `tiene_alergenos: bool`.
- **Nuevos métodos de repositorio** en `ProductoRepository` — `list_public(filtros, page, size)` con joins a `producto_ingredientes` e `ingredientes` para filtrar alérgenos, y `get_detalle_public(id)` que carga relaciones.
- **Nuevo service** `listar_publico` y `obtener_detalle_publico` en `ProductoService` para encapsular la lógica de visibilidad (`deleted_at IS NULL`, `disponible = True` por defecto).
- **Sin nuevas migraciones** — no se agregan columnas ni tablas; todos los datos necesarios ya existen.

## Capabilities

### New Capabilities

- `public-product-catalog`: Exposición de endpoints públicos de lectura del catálogo de productos con paginación, filtros compuestos (categoría, precio, alérgenos, búsqueda de texto) y detalle enriquecido con categorías e ingredientes.

### Modified Capabilities

<!-- No existing specs change their requirements. The new endpoints extend the
     productos module with read-only public access without altering any existing
     ADMIN/STOCK behavior. -->

## Impact

- **`backend/productos/schemas.py`** — agregar `ProductoDetalleRead` y opcionalmente `ProductoFiltros` (query params model).
- **`backend/productos/repository.py`** — agregar `list_public()` y `get_detalle_public()`.
- **`backend/productos/service.py`** — agregar `listar_publico()` y `obtener_detalle_publico()`.
- **`backend/productos/router.py`** — agregar `GET /` y `GET /{id}` sin autenticación. Registrar en el mismo router existente (no nuevo prefijo).
- **Sin cambios en modelos ni migraciones** — `Producto`, `ProductoCategoria`, `ProductoIngrediente` ya tienen todos los campos necesarios.
- **Sin cambios en `backend/categorias/` ni `backend/ingredientes/`** — se reúsan sus schemas (`CategoriaRead`, `ProductoIngredienteRead`) en la respuesta del detalle.
