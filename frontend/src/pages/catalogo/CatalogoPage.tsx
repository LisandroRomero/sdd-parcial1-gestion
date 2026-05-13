import { useSearchParams } from 'react-router-dom'
import type { ProductoFiltros } from '@/entities/producto'
import { useProductos } from '@/features/catalogo'
import { ProductGrid, CatalogFilters, CatalogPagination } from '@/features/catalogo'

function parseFiltersFromURL(params: URLSearchParams): ProductoFiltros {
  const filtros: ProductoFiltros = {}

  const page = params.get('page')
  filtros.page = page ? parseInt(page, 10) : 1

  const size = params.get('size')
  filtros.size = size ? parseInt(size, 10) : 20

  const categoriaId = params.get('categoria_id')
  if (categoriaId) filtros.categoria_id = parseInt(categoriaId, 10)

  const precioMin = params.get('precio_min')
  if (precioMin) filtros.precio_min = parseFloat(precioMin)

  const precioMax = params.get('precio_max')
  if (precioMax) filtros.precio_max = parseFloat(precioMax)

  const busqueda = params.get('busqueda')
  if (busqueda) filtros.busqueda = busqueda

  const tieneAlergenos = params.get('tiene_alergenos')
  if (tieneAlergenos !== null) filtros.tiene_alergenos = tieneAlergenos === 'true'

  return filtros
}

export function CatalogoPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const filtros = parseFiltersFromURL(searchParams)

  const { data, isLoading } = useProductos(filtros)

  const currentPage = filtros.page ?? 1
  const totalPages = data?.pages ?? 1

  function handlePageChange(page: number) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.set('page', String(page))
      return next
    })
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Catálogo</h1>
        {data && (
          <p className="text-sm text-gray-500 mt-1">
            {data.total} {data.total === 1 ? 'producto' : 'productos'} encontrados
          </p>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar filters */}
        <aside className="w-full lg:w-64 shrink-0">
          <CatalogFilters />
        </aside>

        {/* Product grid */}
        <div className="flex-1 min-w-0">
          <ProductGrid items={data?.items ?? []} isLoading={isLoading} />
          {data && (
            <CatalogPagination
              page={currentPage}
              pages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </div>
    </div>
  )
}
