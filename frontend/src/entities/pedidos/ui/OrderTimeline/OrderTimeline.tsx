import { HistorialEstadoRead } from '../../types'
import { statusColors, statusLabels } from '../../constants'

interface OrderTimelineProps {
  historial: HistorialEstadoRead[]
}

const formatDate = (dateString: string) =>
  new Intl.DateTimeFormat('es-AR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(dateString))

const dotBgColor = (estado: string) => {
  return (statusColors[estado] ?? '').split(' ')[0] || 'bg-gray-400'
}

export function OrderTimeline({ historial }: OrderTimelineProps) {
  if (historial.length === 0) return null

  return (
    <div className="space-y-0">
      {historial.map((h, idx) => (
        <div key={h.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`w-3 h-3 rounded-full mt-1.5 ring-2 ring-white ${dotBgColor(h.estado_hasta)}`}
            />
            {idx < historial.length - 1 && (
              <div className="w-0.5 flex-1 bg-gray-200 min-h-[2rem]" />
            )}
          </div>
          <div className={`flex-1 ${idx < historial.length - 1 ? 'pb-4' : ''}`}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-900">
                {statusLabels[h.estado_hasta] ?? h.estado_hasta}
              </span>
              {h.estado_desde && (
                <span className="text-xs text-gray-400">
                  (desde {statusLabels[h.estado_desde] ?? h.estado_desde})
                </span>
              )}
            </div>
            {h.motivo && (
              <p className="text-sm text-gray-500 mt-0.5">{h.motivo}</p>
            )}
            <p className="text-xs text-gray-400 mt-1">{formatDate(h.created_at)}</p>
            {h.usuario_id && (
              <p className="text-xs text-gray-400">Usuario ID: {h.usuario_id}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
