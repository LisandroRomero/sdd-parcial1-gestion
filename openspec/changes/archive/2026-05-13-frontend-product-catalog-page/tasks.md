## 1. Tipos y API layer (entities/producto)

- [x] 1.1 Agregar tipos `ProductoFiltros` y `ProductoPaginado` en `frontend/src/entities/producto/types.ts`
- [x] 1.2 Crear `frontend/src/entities/producto/api.ts` con las funciones `fetchProductos`, `fetchProductoDetalle` y `fetchCategorias` usando la instancia Axios de `shared/api/axios.ts`
- [x] 1.3 Actualizar el barrel `frontend/src/entities/producto/index.ts` para exportar los nuevos tipos y funciones de API

## 2. Hooks TanStack Query (features/catalogo/hooks)

- [x] 2.1 Crear `frontend/src/features/catalogo/hooks/useProductos.ts` con `useQuery` y `queryKey: ['productos', filters]`
- [x] 2.2 Crear `frontend/src/features/catalogo/hooks/useCategorias.ts` con `useQuery`, `queryKey: ['categorias']` y `staleTime: Infinity`
- [x] 2.3 Crear `frontend/src/features/catalogo/hooks/useProductoDetalle.ts` con `useQuery` y `enabled: id > 0`
- [x] 2.4 Crear barrel `frontend/src/features/catalogo/hooks/index.ts` exportando los tres hooks

## 3. Componentes del catálogo (features/catalogo/components)

- [x] 3.1 Crear `frontend/src/features/catalogo/components/ProductCard.tsx` — card con imagen/placeholder, nombre, precio formateado ARS, link a `/catalogo/:id`, hover lift effect
- [x] 3.2 Crear `frontend/src/features/catalogo/components/ProductCardSkeleton.tsx` — skeleton animado con shimmer effect con las mismas dimensiones del ProductCard
- [x] 3.3 Crear `frontend/src/features/catalogo/components/ProductGrid.tsx` — grid responsivo que renderiza `ProductCard` o skeletons según `isLoading`, y `EmptyState` cuando items vacíos
- [x] 3.4 Crear `frontend/src/features/catalogo/components/CatalogFilters.tsx` — panel con Input de búsqueda, select de categoría (usando `useCategorias`), inputs de precio min/max, checkbox de alérgenos, y botón "Limpiar filtros"; todos los cambios actualizan `useSearchParams` con `page=1`
- [x] 3.5 Crear `frontend/src/features/catalogo/components/CatalogPagination.tsx` — botones anterior/siguiente con estado deshabilitado en límites, actualiza query param `page` en URL
- [x] 3.6 Crear barrel `frontend/src/features/catalogo/components/index.ts` exportando todos los componentes
- [x] 3.7 Crear barrel `frontend/src/features/catalogo/index.ts` exportando componentes y hooks de la feature

## 4. Páginas del catálogo (pages/catalogo)

- [x] 4.1 Crear `frontend/src/pages/catalogo/CatalogoPage.tsx` — lee filtros desde `useSearchParams`, orquesta `CatalogFilters` + `ProductGrid` + `CatalogPagination`, muestra EmptyState cuando no hay resultados
- [x] 4.2 Implementar función utilitaria `parseFiltersFromURL(params: URLSearchParams): ProductoFiltros` en `CatalogoPage.tsx` o en un archivo de utils de la feature
- [x] 4.3 Crear `frontend/src/pages/catalogo/ProductoDetallePage.tsx` — lee `id` con `useParams`, usa `useProductoDetalle`, muestra imagen, nombre, descripción, precio, categorías (badges), ingredientes (con badges de alérgenos amber), `AddToCartButton`, botón "Volver al catálogo"
- [x] 4.4 Crear barrel `frontend/src/pages/catalogo/index.ts` exportando `CatalogoPage` y `ProductoDetallePage`

## 5. Router — registrar rutas públicas del catálogo

- [x] 5.1 Actualizar `frontend/src/app/router.tsx` para agregar un grupo de rutas públicas (sin `ProtectedRoute`) que use el `Layout` existente
- [x] 5.2 Registrar `path: '/catalogo'` → `CatalogoPage` (lazy import)
- [x] 5.3 Registrar `path: '/catalogo/:id'` → `ProductoDetallePage` (lazy import)

## 6. Layout — link de navegación al catálogo

- [x] 6.1 Actualizar `frontend/src/app/routes/layout.tsx` para agregar link "Catálogo" en el header que navega a `/catalogo`, usando `NavLink` de React Router con estilo activo cuando la ruta comienza con `/catalogo`
