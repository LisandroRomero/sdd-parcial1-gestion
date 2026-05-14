import { useNavigate } from 'react-router-dom'
import { statusColors, statusLabels } from '../../constants'
import type { PedidoRead } from '../../types'

const formatARS = (value: string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))

const formatDate = (dateString: string) =>
  new Intl.DateTimeFormat('es-AR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(dateString))

interface OrderCardProps {
  pedido: PedidoRead
}

export function OrderCard({ pedido }: OrderCardProps) {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      onClick={() => navigate(`/pedidos/${pedido.id}`)}
      className="w-full text-left bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md hover:border-gray-300 transition-all focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-sm text-gray-500">Pedido #{pedido.id}</p>
          <p className="text-lg font-semibold text-gray-900 mt-0.5">
            {formatARS(pedido.total)}
          </p>
        </div>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
            statusColors[pedido.estado_actual] ?? 'bg-gray-100 text-gray-800 border-gray-300'
          }`}
        >
          {statusLabels[pedido.estado_actual] ?? pedido.estado_actual}
        </span>
      </div>

      <div className="flex items-center gap-4 text-sm text-gray-500">
        <span>{formatDate(pedido.created_at)}</span>
        <span className="text-gray-300">|</span>
        <span>
          Envío: {formatARS(pedido.costo_envio)}
        </span>
      </div>
    </button>
  )
}

/** Skeleton placeholder for loading state. */
export function OrderCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 animate-pulse">
      <div className="flex items-start justify-between mb-3">
        <div className="space-y-2">
          <div className="h-3 w-20 bg-gray-200 rounded" />
          <div className="h-5 w-32 bg-gray-200 rounded" />
        </div>
        <div className="h-6 w-24 bg-gray-200 rounded-full" />
      </div>
      <div className="flex items-center gap-4">
        <div className="h-3 w-40 bg-gray-200 rounded" />
        <div className="h-3 w-24 bg-gray-200 rounded" />
      </div>
    </div>
  )
}
