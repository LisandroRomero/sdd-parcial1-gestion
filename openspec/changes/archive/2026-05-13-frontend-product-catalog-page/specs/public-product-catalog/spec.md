## ADDED Requirements

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
