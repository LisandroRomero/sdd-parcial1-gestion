import { useEffect, useState } from 'react'
import { initMercadoPago, CardPayment } from '@mercadopago/sdk-react'
import { usePaymentStore } from '@/shared/lib/stores/payment.store'
import { crearPago } from '@/shared/api/pagos.api'
import { Button, Card, CardContent } from '@/shared/components'
import { ErrorMessage, LoadingSpinner } from '@/shared/ui'

const MP_KEY = import.meta.env.VITE_MP_PUBLIC_KEY

interface CardTokenizationFormProps {
  pedidoId: number
  total: string
  onApproved: (paymentId: number) => void
  onRejected: (error: string) => void
  onPending: (paymentId: number) => void
  onCancel: () => void
}

const formatARS = (value: string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))

export function CardTokenizationForm({ pedidoId, total, onApproved, onRejected, onPending, onCancel }: CardTokenizationFormProps) {
  const { status, setProcessing } = usePaymentStore()
  const [initError, setInitError] = useState<string | null>(null)

  useEffect(() => {
    if (!MP_KEY) {
      setInitError('La clave pública de Mercado Pago no está configurada.')
      return
    }
    try {
      initMercadoPago(MP_KEY, { locale: 'es-AR' })
    } catch {
      setInitError('Error al inicializar Mercado Pago.')
    }
  }, [])

  if (initError) {
    return (
      <div className="max-w-md mx-auto py-8">
        <Card>
          <CardContent className="py-6">
            <ErrorMessage message={initError} />
            <div className="mt-4 flex justify-center">
              <Button variant="ghost" onClick={onCancel}>Volver</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleSubmit = async (cardData: { token: string; payment_method_id: string }) => {
    setProcessing()
    try {
      const response = await crearPago({
        pedido_id: pedidoId,
        card_token: cardData.token,
        payment_method_id: cardData.payment_method_id,
        monto: total,
      })
      const mpStatus = response.mp_status ?? 'pending'
      if (mpStatus === 'approved') {
        onApproved(response.id)
      } else if (mpStatus === 'rejected') {
        onRejected('El pago fue rechazado. Verificá los datos e intentá de nuevo.')
      } else {
        onPending(response.id)
      }
    } catch {
      onRejected('Error al procesar el pago. Verificá tu conexión e intentá de nuevo.')
    }
  }

  const handleError = () => {
    onRejected('Error inesperado en el formulario de pago.')
  }

  const isProcessing = status === 'processing'

  return (
    <div className="max-w-lg mx-auto py-8">
      <Card>
        <CardContent className="py-6 space-y-6">
          <div className="text-center">
            <h2 className="text-xl font-bold text-gray-900 mb-2">Completar pago</h2>
            <p className="text-gray-600">
              Total a pagar:{' '}
              <span className="font-semibold text-gray-900">{formatARS(total)}</span>
            </p>
          </div>

          <CardPayment
            initialization={{ amount: parseFloat(total) }}
            customization={{ visual: { style: { theme: 'default' } } }}
            onSubmit={handleSubmit}
            onError={handleError}
          />

          {isProcessing && (
            <div className="flex items-center justify-center gap-2 text-gray-600">
              <LoadingSpinner size="sm" />
              <span>Procesando pago...</span>
            </div>
          )}

          <div className="flex justify-center">
            <Button variant="ghost" onClick={onCancel} disabled={isProcessing}>
              Cancelar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
