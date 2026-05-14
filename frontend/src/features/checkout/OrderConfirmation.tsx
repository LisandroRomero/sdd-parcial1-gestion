import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/shared/components'
import { Button } from '@/shared/components'

interface OrderConfirmationProps {
  pedidoId: number
  total: string
}

export function OrderConfirmation({ pedidoId, total }: OrderConfirmationProps) {
  const navigate = useNavigate()

  const formatARS = (value: string) =>
    new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))

  return (
    <div className="max-w-lg mx-auto text-center py-8">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span className="text-3xl text-green-600">✓</span>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Pedido confirmado!</h2>
      <p className="text-gray-600 mb-6">Tu pedido fue creado con éxito.</p>

      <Card className="mb-8">
        <CardContent className="py-6 space-y-2">
          <p className="text-sm text-gray-500">Número de pedido</p>
          <p className="text-3xl font-bold text-gray-900">#{pedidoId}</p>
          <p className="text-lg font-semibold text-gray-700">{formatARS(total)}</p>
        </CardContent>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        {pedidoId > 0 && (
          <Button onClick={() => navigate(`/pedidos/${pedidoId}`)} variant="outline" size="lg">
            Ver detalle del pedido
          </Button>
        )}
        <Button onClick={() => navigate('/catalogo')} variant="primary" size="lg">
          Volver al catálogo
        </Button>
      </div>
    </div>
  )
}
