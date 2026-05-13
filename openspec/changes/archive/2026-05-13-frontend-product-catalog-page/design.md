## Context

El backend de catálogo público está completamente implementado (Epic 2.5): `GET /api/v1/productos` con paginación y filtros, `GET /api/v1/productos/{id}` con detalle completo, y `GET /api/v1/categorias`. El frontend ya tiene:
- Tipos `ProductoRead`, `ProductoDetalleRead`, `CategoriaRead`, `ProductoIngredienteRead` en `entities/producto/types.ts`
- `AddToCartButton` en `features/carrito/components/AddToCartButton.tsx` — listo para usar
- Shared components: `Button`, `Card`, `Input`, `LoadingSpinner`, `EmptyState`
- Axios con interceptor JWT en `shared/api/axios.ts`

El router actual solo tiene rutas protegidas (`/`, `/login`, `/register`). Las rutas de catálogo deben ser **públicas** (sin login requerido).

## Goals / Non-Goals

**Goals:**
- Página `/catalogo` pública con grid de productos, filtros funcionales, paginación
- Filtros en URL (query params) para compartibilidad y back-navigation
- Página `/catalogo/:id` pública con detalle del producto + AddToCartButton
- Skeleton loading y estado vacío con UX apropiada
- FSD estricto: código bajo `features/catalogo/` y `pages/catalogo/`

**Non-Goals:**
- Checkout/confirmación de pedido (Epic futura)
- Reseñas o ratings de productos
- Comparador de productos
- Favoritos / wishlist
- Ordenamiento (sort) de resultados — solo paginación y filtros básicos

## Decisions

### D1: Filtros en URL con `useSearchParams` (React Router v6)

**Decisión:** Los filtros activos viven en la URL como query params, no en estado local de React.

**Rationale:** Permite compartir URLs con filtros aplicados (`/catalogo?busqueda=pizza&categoria_id=3`), preserva el estado al navegar hacia atrás desde el detalle, y elimina la necesidad de un store de Zustand adicional para filtros.

**Alternativa considerada:** `useState` local para los filtros — descartada porque no permite back-navigation ni URLs compartibles.

**Alternativa considerada:** Zustand store para filtros — descartada porque el estado del servidor no debe duplicarse en Zustand (convención del proyecto: TanStack Query para estado de servidor).

### D2: Datos con TanStack Query

**Decisión:** Usar `useQuery` para el listado y el detalle de productos. Los filtros de la URL se pasan como `queryKey` para que TanStack Query revalide automáticamente al cambiar filtros.

**Rationale:** Es la convención del proyecto. Provee caching, loading/error states, y revalidación declarativa sin escribir boilerplate.

```typescript
// queryKey incluye los filtros para revalidación automática
const { data, isLoading } = useQuery({
  queryKey: ['productos', filters],
  queryFn: () => fetchProductos(filters),
})
```

### D3: Estructura FSD para la feature

**Decisión:** Crear `frontend/src/features/catalogo/` con subcarpetas `components/` y `hooks/`. Las páginas van en `frontend/src/pages/catalogo/`.

```
features/catalogo/
  components/
    ProductCard.tsx         — card individual del grid
    ProductGrid.tsx         — grid con estado loading/vacío
    CatalogFilters.tsx      — panel de filtros (búsqueda, categoría, precio, alérgenos)
    ProductCardSkeleton.tsx — skeleton para el estado de carga
    CatalogPagination.tsx   — navegación de páginas
  hooks/
    useProductos.ts         — TanStack Query para listado
    useCategorias.ts        — TanStack Query para categorías (filtro)
    useProductoDetalle.ts   — TanStack Query para detalle

pages/catalogo/
  CatalogoPage.tsx          — página /catalogo
  ProductoDetallePage.tsx   — página /catalogo/:id
```

**Rationale:** FSD estricto — pages solo orquestan, features contienen la lógica encapsulada.

### D4: API layer en `entities/producto/api.ts`

**Decisión:** Las funciones de fetching viven en `frontend/src/entities/producto/api.ts`, no inline en los hooks.

**Rationale:** Separa el contrato de API de la lógica de estado. Los hooks de TanStack Query importan desde la entidad. Es más testeable y reutilizable.

```typescript
// entities/producto/api.ts
export async function fetchProductos(filters: ProductoFiltros): Promise<ProductoPaginado>
export async function fetchProductoDetalle(id: number): Promise<ProductoDetalleRead>
```

### D5: Rutas públicas sin `ProtectedRoute`

**Decisión:** Las rutas `/catalogo` y `/catalogo/:id` se agregan fuera del wrapper `ProtectedRoute`, en un grupo de rutas públicas con `Layout` opcional.

**Rationale:** El catálogo debe ser accesible sin login. El `router.tsx` actual ya tiene un patrón de rutas públicas (`/login`, `/register`). Las rutas del catálogo usan el mismo layout de header (para mostrar el CartBadge) pero sin el guard de autenticación.

**Implementación:** Crear un grupo de rutas públicas que sí usa `Layout` (para header/navegación) pero sin `ProtectedRoute`.

### D6: Diseño visual — aesthetic "warm food marketplace"

**Decisión:** Palette cálida (ambers, oranges, creams) con tipografía limpia. Cards con hover lift effect. Skeleton con shimmer animation. Badge de alérgenos en amber/orange. Filtros en sidebar colapsable en mobile.

**Rationale:** El contexto es food e-commerce. La paleta cálida evoca apetito y calidez. Contrasta con el fondo neutro del layout actual (`bg-gray-50`).

## Risks / Trade-offs

- **[Riesgo] Filtro de categorías hace una query extra** → Mitigación: `staleTime: Infinity` en `useCategorias` — las categorías no cambian frecuentemente.
- **[Trade-off] useSearchParams como estado de filtros** → Obliga a parsear strings desde la URL (ej: `categoria_id` viene como string). Se define una función `parseFiltersFromURL(params)` para centralizar el parsing.
- **[Riesgo] AddToCartButton requiere `ProductoDetalleRead`** → La página `/catalogo` solo tiene `ProductoRead` (sin ingredientes). El CTA desde el grid debe navegar al detalle, no agregar directo desde el card. Solo desde `/catalogo/:id` se usa AddToCartButton.
- **[Trade-off] No hay route guard en /catalogo** → El CartBadge en el header requiere el Layout compartido. El usuario puede ver el catálogo sin login pero al hacer checkout se le pedirá autenticación (flujo futuro).

## Migration Plan

1. Crear `entities/producto/api.ts` con las funciones de fetch
2. Crear feature `catalogo/` con componentes y hooks
3. Crear páginas en `pages/catalogo/`
4. Actualizar `router.tsx` para registrar `/catalogo` y `/catalogo/:id`
5. Actualizar `layout.tsx` para agregar link de navegación al catálogo
6. Sin rollback necesario — adición pura, sin modificar lógica existente

## Open Questions

- ¿El layout del catálogo usa el mismo `<Layout>` del dashboard (con header y CartBadge)? **Sí** — decisión D5 establece rutas públicas con Layout.
- ¿Cuántos productos por página por defecto? **20** (same as backend default).
- ¿El link al catálogo en el header es visible para usuarios no autenticados? **Sí** — el catálogo es público.
