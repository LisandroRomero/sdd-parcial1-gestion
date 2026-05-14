import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useListarPedidos } from '@/features/pedidos/hooks/useListarPedidos'
import { OrderCard, OrderCardSkeleton } from '@/entities/pedidos/ui/OrderCard'
import { OrderFilters } from '@/features/pedidos/components/OrderFilters'
import { OrderPagination } from '@/features/pedidos/components/OrderPagination'
import { ErrorMessage, EmptyState } from '@/shared/ui'
import { Button } from '@/shared/components'

interface Filters {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
}

export function PedidoListPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<Filters>({})
  const size = 20

  const { data, isLoading, isError, error, refetch } = useListarPedidos({
    params: { ...filters, page, size },
  })

  function handleFilterChange(newFilters: Filters) {
    setFilters(newFilters)
    setPage(1)
  }

  // --- Loading state ---
  if (isLoading && !data) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Pedidos</h1>
        <div className="space-y-4">
          {Array.from({ length: 4 }, (_, i) => (
            <OrderCardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  // --- Error state ---
  if (isError && !data) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Pedidos</h1>
        <ErrorMessage
          message={error instanceof Error ? error.message : 'Error al cargar los pedidos'}
          onRetry={refetch}
        />
      </div>
    )
  }

  const pedidos = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 0

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Pedidos</h1>

      {/* Filters */}
      <div className="mb-6">
        <OrderFilters onFilterChange={handleFilterChange} />
      </div>

      {/* Empty state */}
      {pedidos.length === 0 && !isLoading ? (
        <EmptyState
          title="No tienes pedidos aún"
          description="Tus pedidos aparecerán acá una vez que realices tu primera compra."
          action={
            <Button variant="primary" onClick={() => navigate('/catalogo')}>
              Ir al catálogo
            </Button>
          }
        />
      ) : (
        <>
          {/* Order list */}
          <div className="space-y-4">
            {pedidos.map((pedido) => (
              <OrderCard key={pedido.id} pedido={pedido} />
            ))}
          </div>

          {/* Pagination */}
          <OrderPagination
            page={page}
            pages={pages}
            total={total}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}
