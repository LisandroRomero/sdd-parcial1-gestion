import { useSearchParams } from 'react-router-dom'
import { ShoppingBag } from 'lucide-react'
import type { ProductoFiltros } from '@/entities/producto'
import { useProductos } from '@/features/catalogo'
import { ProductGrid, CatalogFilters, CatalogPagination } from '@/features/catalogo'
import { Button } from '@/shared/components'
import { ErrorMessage, OfflineMessage, LoadingSpinner } from '@/shared/ui'
import { useOffline } from '@/shared/lib/hooks'
import { getErrorMessage } from '@/shared/api'

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
  const isOffline = useOffline()

  const { data, isLoading, isError, error, refetch } = useProductos(filtros)

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
      <div className="mb-6 flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 text-white">
          <ShoppingBag size={20} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Catálogo</h1>
          {data && (
            <p className="text-sm text-gray-500">
              {data.total} {data.total === 1 ? 'producto' : 'productos'} disponibles
            </p>
          )}
        </div>
      </div>

      {isOffline && (
        <div className="mb-6">
          <OfflineMessage />
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar filters */}
        <aside className="w-full lg:w-64 shrink-0">
          <CatalogFilters />
        </aside>

        {/* Product grid */}
        <div className="flex-1 min-w-0">
          {isLoading && !data && (
            <div className="mb-4 flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          )}
          {isError && !data ? (
            <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} className="mb-4" />
          ) : null}
          <ProductGrid
            items={data?.items ?? []}
            isLoading={isLoading}
            emptyAction={
              <Button
                variant="outline"
                onClick={() =>
                  setSearchParams((prev) => {
                    const next = new URLSearchParams(prev)
                    next.delete('categoria_id')
                    next.delete('precio_min')
                    next.delete('precio_max')
                    next.delete('busqueda')
                    next.delete('tiene_alergenos')
                    next.set('page', '1')
                    return next
                  })
                }
              >
                Limpiar filtros
              </Button>
            }
          />
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
