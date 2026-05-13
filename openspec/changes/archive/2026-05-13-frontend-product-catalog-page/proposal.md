## Why

El backend de catálogo público (Epic 2.5) ya está implementado y funcional. Sin una página de catálogo en el frontend, los usuarios no tienen forma de explorar y agregar productos al carrito — el flujo de compra está bloqueado. Esta es la vista pública central del e-commerce.

## What Changes

- Nueva página `/catalogo` (pública, sin login requerido): grid de productos con filtros interactivos
  - Filtros: búsqueda por texto, categoría, rango de precio, `tiene_alergenos`
  - Filtros persisten en URL como query params (`?busqueda=pizza&categoria_id=3`) para compartibilidad y back-navigation
  - Paginación con navegación de páginas
  - `ProductCard` con imagen (o placeholder), nombre, precio formateado, badge de alérgenos
  - Estado de loading con skeleton grid y estado vacío con CTA
- Nueva página `/catalogo/:id` (pública): detalle completo de un producto
  - Muestra ingredientes con badges de alérgenos por cada ítem
  - Muestra categorías del producto
  - Integra `AddToCartButton` ya existente de Epic 4.1
  - Botón "Volver al catálogo" con query params preservados
- Nueva feature `catalogo` bajo FSD en `frontend/src/features/catalogo/`
- Nueva entidad `api` en `frontend/src/entities/producto/api.ts` con funciones de fetching de productos y categorías
- Actualización de `router.tsx` para registrar las rutas `/catalogo` y `/catalogo/:id`
- Actualización del layout para agregar link de navegación al catálogo

## Capabilities

### New Capabilities

- `product-catalog-page`: Páginas de catálogo y detalle de producto en el frontend, incluyendo filtros por URL, paginación, skeletons, y estado vacío.

### Modified Capabilities

- `public-product-catalog`: Agregar requisitos de frontend (queries TanStack, tipos de filtros, contratos de componentes UI)

## Impact

- **Nuevos archivos**: `frontend/src/features/catalogo/` (componentes y hooks), `frontend/src/entities/producto/api.ts` (funciones de API), `frontend/src/pages/catalogo/` (páginas)
- **Archivos modificados**: `frontend/src/app/router.tsx` (registrar rutas), `frontend/src/app/routes/layout.tsx` (agregar nav link)
- **APIs consumidas**: `GET /api/v1/productos` (listado + filtros), `GET /api/v1/productos/{id}` (detalle), `GET /api/v1/categorias` (para select de filtro)
- **Dependencias activas**: TanStack Query (fetching), React Router v6 `useSearchParams` (filtros en URL), componentes shared existentes (Button, Card, Input, LoadingSpinner, EmptyState)
- **Sin dependencias nuevas de npm** — todo se resuelve con lo ya instalado
