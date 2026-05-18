import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/shared/components'
import { Button } from '@/shared/components'

interface OrderConfirmationProps {
  pedidoId: number
  total: string
  paymentStatus?: 'approved' | 'rejected' | 'pending'
  paymentId?: number | null
  onRetry?: () => void
}

export function OrderConfirmation({ pedidoId, total, paymentStatus, paymentId, onRetry }: OrderConfirmationProps) {
  const navigate = useNavigate()

  const formatARS = (value: string) =>
    new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))

  const iconBg = !paymentStatus || paymentStatus === 'approved' ? 'bg-green-100' : paymentStatus === 'rejected' ? 'bg-red-100' : 'bg-yellow-100'
  const iconColor = !paymentStatus || paymentStatus === 'approved' ? 'text-green-600' : paymentStatus === 'rejected' ? 'text-red-600' : 'text-yellow-600'
  const iconText = !paymentStatus || paymentStatus === 'approved' ? '✓' : paymentStatus === 'rejected' ? '✕' : '⏳'

  return (
    <div className="max-w-lg mx-auto text-center py-8">
      <div className={`w-16 h-16 ${iconBg} rounded-full flex items-center justify-center mx-auto mb-6`}>
        <span className={`text-3xl ${iconColor}`}>{iconText}</span>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        {paymentStatus === 'rejected' ? 'Pago rechazado' : '¡Pedido confirmado!'}
      </h2>
      <p className="text-gray-600 mb-6">
        {paymentStatus === 'rejected'
          ? 'El pago no pudo ser procesado.'
          : paymentStatus === 'pending'
            ? 'El pago está en proceso.'
            : 'Tu pedido fue creado con éxito.'}
      </p>

      {paymentStatus && (
        <div className="mb-4">
          {paymentStatus === 'approved' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-green-100 text-green-800">
              {'✅'} Pago aprobado{paymentId != null && ` (ID: ${paymentId})`}
            </span>
          )}
          {paymentStatus === 'rejected' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-red-100 text-red-800">
              {'❌'} Pago rechazado
            </span>
          )}
          {paymentStatus === 'pending' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
              {'⏳'} Pago en proceso
            </span>
          )}
        </div>
      )}

      {paymentStatus === 'pending' && (
        <p className="text-sm text-gray-500 mb-6">
          El pago está siendo procesado. Te notificaremos cuando se confirme.
        </p>
      )}

      <Card className="mb-8">
        <CardContent className="py-6 space-y-2">
          <p className="text-sm text-gray-500">Número de pedido</p>
          <p className="text-3xl font-bold text-gray-900">#{pedidoId}</p>
          <p className="text-lg font-semibold text-gray-700">{formatARS(total)}</p>
        </CardContent>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        {paymentStatus === 'rejected' && onRetry && (
          <Button onClick={onRetry} variant="primary" size="lg">
            Reintentar
          </Button>
        )}
        {pedidoId > 0 && (
          <Button onClick={() => navigate(`/pedidos/${pedidoId}`)} variant="outline" size="lg">
            Ver detalle del pedido
          </Button>
        )}
        <Button onClick={() => navigate('/catalogo')} variant="primary" size="lg">
          {paymentStatus === 'rejected' ? 'Ir al catálogo' : 'Volver al catálogo'}
        </Button>
      </div>
    </div>
  )
}
