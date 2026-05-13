## ADDED Requirements

### Requirement: Entidad producto — API layer frontend
El frontend SHALL definir las funciones de acceso a la API en `frontend/src/entities/producto/api.ts`. Las funciones SHALL usar la instancia Axios de `shared/api/axios.ts`. Se SHALL exportar:
- `fetchProductos(filters: ProductoFiltros): Promise<ProductoPaginado>` — llama a `GET /api/v1/productos` con los filtros como query params
- `fetchProductoDetalle(id: number): Promise<ProductoDetalleRead>` — llama a `GET /api/v1/productos/{id}`
- `fetchCategorias(): Promise<CategoriaRead[]>` — llama a `GET /api/v1/categorias` y retorna el array de categorías

El tipo `ProductoFiltros` SHALL ser definido en `frontend/src/entities/producto/types.ts`:
```typescript
interface ProductoFiltros {
  page?: number
  size?: number
  categoria_id?: number
  precio_min?: number
  precio_max?: number
  busqueda?: string
  tiene_alergenos?: boolean
}
```

El tipo `ProductoPaginado` SHALL ser definido en `frontend/src/entities/producto/types.ts`:
```typescript
interface ProductoPaginado {
  items: ProductoRead[]
  total: number
  page: number
  size: number
  pages: number
}
```

#### Scenario: fetchProductos sin filtros retorna primera página
- **WHEN** `fetchProductos({})` es llamado
- **THEN** se realiza `GET /api/v1/productos` sin query params adicionales
- **THEN** retorna un objeto `ProductoPaginado` con `items`, `total`, `page`, `size`, `pages`

#### Scenario: fetchProductos con filtros serializa correctamente
- **WHEN** `fetchProductos({ busqueda: 'pizza', categoria_id: 3, page: 2 })` es llamado
- **THEN** la request incluye `?busqueda=pizza&categoria_id=3&page=2` en la URL

#### Scenario: fetchProductoDetalle retorna ProductoDetalleRead
- **WHEN** `fetchProductoDetalle(5)` es llamado
- **THEN** se realiza `GET /api/v1/productos/5`
- **THEN** retorna un objeto `ProductoDetalleRead` con `ingredientes`, `categorias`, `tiene_alergenos`

#### Scenario: fetchCategorias retorna array de categorías
- **WHEN** `fetchCategorias()` es llamado
- **THEN** se realiza `GET /api/v1/categorias`
- **THEN** retorna un array de `CategoriaRead`

---

### Requirement: Feature catálogo — hooks TanStack Query
El frontend SHALL definir los siguientes hooks en `frontend/src/features/catalogo/hooks/`:

- `useProductos(filters: ProductoFiltros)` — usa `useQuery` con `queryKey: ['productos', filters]` y `queryFn: fetchProductos(filters)`. SHALL retornar `{ data, isLoading, isError, error }`.
- `useCategorias()` — usa `useQuery` con `queryKey: ['categorias']`, `queryFn: fetchCategorias`, y `staleTime: Infinity`. SHALL retornar `{ data, isLoading }`.
- `useProductoDetalle(id: number)` — usa `useQuery` con `queryKey: ['productos', id]` y `queryFn: fetchProductoDetalle(id)`. SHALL estar habilitado solo cuando `id` sea un número válido (> 0).

#### Scenario: useProductos revalida al cambiar filtros
- **WHEN** el valor de `filters` cambia (ej: el usuario cambia la búsqueda)
- **THEN** TanStack Query detecta el cambio en el `queryKey` y ejecuta un nuevo fetch automáticamente

#### Scenario: useCategorias usa caché permanente
- **WHEN** `useCategorias()` es montado por segunda vez en la misma sesión
- **THEN** NO se realiza un segundo fetch — los datos se sirven desde el caché (staleTime: Infinity)

#### Scenario: useProductoDetalle con id inválido no hace fetch
- **WHEN** `useProductoDetalle(0)` o `useProductoDetalle(NaN)` es llamado
- **THEN** la query está deshabilitada y NO realiza ninguna request HTTP

---

### Requirement: Componente ProductCard
El frontend SHALL implementar el componente `ProductCard` en `frontend/src/features/catalogo/components/ProductCard.tsx`.

El componente SHALL recibir `producto: ProductoRead` como prop y SHALL:
1. Mostrar la imagen del producto (`imagen_url`) o un placeholder visual si `imagen_url` es null
2. Mostrar el nombre del producto (`nombre`)
3. Mostrar el precio formateado como moneda ARS (ej: `$1.500,00`)
4. Mostrar un badge "Contiene alérgenos" visible solo si el producto tiene alérgenos — NOTE: `ProductoRead` NO incluye `tiene_alergenos`. El badge de alérgenos en el grid es opcional/no aplicable desde el listado paginado; se muestra en detalle.
5. Ser un link clickeable que navega a `/catalogo/:id`
6. Tener hover state visual (lift effect con shadow)

Corrección: dado que `ProductoRead` no incluye `tiene_alergenos`, el badge de alérgenos NO se muestra en `ProductCard`. Solo se muestra en `ProductoDetallePage`.

#### Scenario: ProductCard muestra placeholder cuando imagen_url es null
- **WHEN** `producto.imagen_url === null`
- **THEN** se renderiza un placeholder visual (ícono o color de fondo) en lugar de un `<img>`

#### Scenario: ProductCard muestra precio formateado
- **GIVEN** `producto.precio_base = "1500.00"`
- **THEN** el componente muestra `$1.500,00`

#### Scenario: ProductCard navega al detalle al hacer click
- **WHEN** el usuario hace click sobre el card
- **THEN** el router navega a `/catalogo/{producto.id}`

---

### Requirement: Componente ProductCardSkeleton
El frontend SHALL implementar `ProductCardSkeleton` en `frontend/src/features/catalogo/components/ProductCardSkeleton.tsx`.

El componente SHALL renderizar una versión skeleton (placeholder animado con shimmer) del `ProductCard` con las mismas dimensiones aproximadas. Se SHALL renderizar un grid de 8 skeletons durante el estado de loading del catálogo.

#### Scenario: Skeleton visible durante isLoading
- **WHEN** `useProductos` retorna `isLoading: true`
- **THEN** se renderiza el grid de skeletons en lugar del grid de productos

#### Scenario: Skeleton no visible cuando isLoading es false
- **WHEN** `useProductos` retorna `isLoading: false`
- **THEN** los skeletons son reemplazados por los `ProductCard` reales o por el estado vacío

---

### Requirement: Componente CatalogFilters
El frontend SHALL implementar `CatalogFilters` en `frontend/src/features/catalogo/components/CatalogFilters.tsx`.

El componente SHALL:
1. Recibir los filtros actuales como props (leídos desde `useSearchParams`)
2. Emitir cambios a través de una función `onFilterChange(filters: Partial<ProductoFiltros>)` que actualiza la URL
3. Incluir: campo de búsqueda por texto (Input), select de categoría (con opciones de `useCategorias()`), inputs de precio mínimo/máximo, checkbox de "solo sin alérgenos"
4. Incluir botón "Limpiar filtros" que resetea todos los params a su estado inicial

Al cambiar cualquier filtro, SHALL resetear `page` a 1 para evitar resultados vacíos.

#### Scenario: Cambio de búsqueda actualiza URL
- **WHEN** el usuario escribe "pizza" en el campo de búsqueda y confirma (debounce o Enter)
- **THEN** la URL se actualiza a incluir `?busqueda=pizza&page=1`
- **THEN** `useProductos` revalida con los nuevos filtros automáticamente

#### Scenario: Limpiar filtros resetea la URL
- **WHEN** el usuario hace click en "Limpiar filtros"
- **THEN** todos los query params de filtros son removidos de la URL
- **THEN** `useProductos` revalida sin filtros

#### Scenario: Filtro de categoría usa opciones cargadas dinámicamente
- **WHEN** `useCategorias()` retorna datos
- **THEN** el select de categoría muestra las opciones cargadas
- **WHEN** `useCategorias()` está loading
- **THEN** el select está deshabilitado con estado de carga visual

---

### Requirement: Componente CatalogPagination
El frontend SHALL implementar `CatalogPagination` en `frontend/src/features/catalogo/components/CatalogPagination.tsx`.

El componente SHALL recibir `currentPage`, `totalPages`, y `onPageChange` como props. SHALL:
1. Mostrar botones de página anterior y siguiente
2. Mostrar el número de página actual y total
3. Deshabilitar "anterior" cuando `currentPage === 1`
4. Deshabilitar "siguiente" cuando `currentPage === totalPages`
5. Al cambiar de página, actualizar el query param `page` en la URL

#### Scenario: Botón anterior deshabilitado en primera página
- **WHEN** `currentPage === 1`
- **THEN** el botón "Anterior" está deshabilitado y no responde a clicks

#### Scenario: Cambio de página actualiza URL y refetch
- **WHEN** el usuario hace click en "Siguiente"
- **THEN** la URL se actualiza con `?page=2`
- **THEN** `useProductos` revalida con `page: 2`

---

### Requirement: Página CatalogoPage (`/catalogo`)
El frontend SHALL implementar `CatalogoPage` en `frontend/src/pages/catalogo/CatalogoPage.tsx`.

La página SHALL:
1. Leer los filtros desde `useSearchParams` y parsearlos a `ProductoFiltros`
2. Pasar los filtros a `useProductos(filters)` para obtener los datos
3. Renderizar `CatalogFilters` en un panel lateral o superior
4. Renderizar `ProductGrid` con los productos o el skeleton grid según `isLoading`
5. Renderizar `CatalogPagination` cuando `data.pages > 1`
6. Mostrar `EmptyState` cuando `data.items.length === 0` y no hay loading
7. Ser accesible públicamente (sin login requerido)

#### Scenario: Estado inicial sin filtros muestra productos disponibles
- **WHEN** el usuario navega a `/catalogo` sin query params
- **THEN** se muestran los productos con `page=1`, `size=20` (defaults del backend)
- **THEN** los filtros están en su estado vacío/default

#### Scenario: Estado vacío cuando no hay resultados
- **WHEN** `data.items.length === 0` y `isLoading === false`
- **THEN** se muestra el componente `EmptyState` con mensaje "No se encontraron productos" y CTA para limpiar filtros

#### Scenario: URL con filtros restaura estado de filtros al cargar
- **WHEN** el usuario navega a `/catalogo?busqueda=pizza&categoria_id=3`
- **THEN** el campo de búsqueda muestra "pizza", el select de categoría muestra la categoría 3
- **THEN** `useProductos` hace fetch con `{ busqueda: 'pizza', categoria_id: 3 }`

---

### Requirement: Página ProductoDetallePage (`/catalogo/:id`)
El frontend SHALL implementar `ProductoDetallePage` en `frontend/src/pages/catalogo/ProductoDetallePage.tsx`.

La página SHALL:
1. Leer el param `id` de la URL con `useParams`
2. Usar `useProductoDetalle(id)` para cargar los datos del producto
3. Mostrar loading spinner mientras `isLoading === true`
4. Mostrar `ErrorMessage` si `isError === true`
5. Mostrar el detalle del producto: imagen, nombre, descripción, precio formateado, categorías como badges, ingredientes como lista con badges de alérgenos
6. Renderizar `AddToCartButton` (ya existente en `features/carrito`) pasando el `producto: ProductoDetalleRead`
7. Incluir botón "Volver al catálogo" que navega a `/catalogo` (preservando los query params anteriores si están disponibles)
8. Ser accesible públicamente (sin login requerido)

El badge de alérgenos SHALL mostrarse para cada ingrediente donde `es_alergeno === true` con estilo visual diferenciado (amber/naranja).

#### Scenario: Carga y muestra detalle del producto
- **WHEN** el usuario navega a `/catalogo/5`
- **THEN** `useProductoDetalle(5)` hace fetch de `GET /api/v1/productos/5`
- **THEN** la página muestra nombre, precio, descripción, categorías, e ingredientes del producto

#### Scenario: Ingredientes con alérgenos muestran badge visual
- **GIVEN** un ingrediente con `es_alergeno === true`
- **THEN** ese ingrediente muestra un badge de alérgeno (ej: ícono de advertencia + texto "alérgeno") con estilo diferenciado

#### Scenario: AddToCartButton integrado correctamente
- **GIVEN** el producto tiene `disponible === true`
- **THEN** el componente `AddToCartButton` es visible y funcional, usando el producto cargado como prop
- **WHEN** el usuario agrega al carrito
- **THEN** el producto se agrega al store y se muestra el toast de confirmación

#### Scenario: Producto no encontrado (404)
- **WHEN** `useProductoDetalle` retorna `isError === true` (backend devolvió 404)
- **THEN** se muestra un mensaje de error con opción de volver al catálogo

---

### Requirement: Actualización de router — rutas públicas del catálogo
El frontend SHALL actualizar `frontend/src/app/router.tsx` para registrar las rutas del catálogo como rutas **públicas** (sin `ProtectedRoute`).

Las rutas SHALL usar el componente `Layout` existente (para mostrar el header con CartBadge y navegación).

Las rutas a agregar:
- `path: '/catalogo'` → `CatalogoPage`
- `path: '/catalogo/:id'` → `ProductoDetallePage`

Ambas páginas SHALL ser importadas con `lazy()` para code splitting.

#### Scenario: Acceso a /catalogo sin autenticación
- **WHEN** un usuario no autenticado navega a `/catalogo`
- **THEN** la página se carga correctamente sin redirigir al login

#### Scenario: Acceso a /catalogo/:id sin autenticación
- **WHEN** un usuario no autenticado navega a `/catalogo/5`
- **THEN** la página de detalle se carga correctamente sin redirigir al login

---

### Requirement: Actualización del layout — link de navegación al catálogo
El frontend SHALL actualizar `frontend/src/app/routes/layout.tsx` para agregar un link de navegación al catálogo en el header.

El link SHALL:
1. Mostrar texto "Catálogo" o similar
2. Navegar a `/catalogo` al hacer click
3. Ser visible tanto para usuarios autenticados como no autenticados
4. Tener estilo activo cuando la ruta actual comience con `/catalogo`

#### Scenario: Link al catálogo visible en el header
- **WHEN** el usuario está en cualquier página que usa el Layout
- **THEN** el header muestra el link al catálogo

#### Scenario: Link activo en ruta del catálogo
- **WHEN** la ruta actual es `/catalogo` o `/catalogo/:id`
- **THEN** el link al catálogo muestra su estado activo visualmente
