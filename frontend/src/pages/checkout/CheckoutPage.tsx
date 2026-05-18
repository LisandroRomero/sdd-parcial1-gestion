import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { usePaymentStore } from '@/shared/lib/stores/payment.store'
import {
  useCheckout,
  CheckoutSummary,
  AddressSelector,
  OrderConfirmation,
  PaymentMethodSelector,
  CardTokenizationForm,
} from '@/features/checkout'
import { Button } from '@/shared/components'
import { LoadingSpinner, EmptyState, ErrorMessage, OfflineMessage, NoPermissionMessage } from '@/shared/ui'
import { getAuthErrorStatus, getErrorMessage } from '@/shared/api'
import { useOffline } from '@/shared/lib/hooks'
import type { PedidoRead } from '@/entities/pedidos'

const formatARS = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)

type CheckoutPhase = 'form' | 'tokenization' | 'result'
type PaymentResultStatus = 'approved' | 'rejected' | 'pending'

interface PaymentResult {
  status: PaymentResultStatus
  paymentId: number | null
  error?: string
}

export function CheckoutPage() {
  const navigate = useNavigate()
  const isCartEmpty = useCartStore((s) => s.isCartEmpty)
  const totalPrice = useCartStore((s) => s.totalPrice)
  const getItemsForCheckout = useCartStore((s) => s.getItemsForCheckout)
  const isOffline = useOffline()
  const { setApproved, setRejected, resetState: resetPaymentState } = usePaymentStore()

  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(null)
  const [selectedFormaPago, setSelectedFormaPago] = useState('EFECTIVO')
  const [checkoutPhase, setCheckoutPhase] = useState<CheckoutPhase>('form')
  const [createdPedido, setCreatedPedido] = useState<PedidoRead | null>(null)
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const checkoutMutation = useCheckout()

  const authStatus = checkoutMutation.isError ? getAuthErrorStatus(checkoutMutation.error) : undefined

  useEffect(() => {
    resetPaymentState()
  }, [resetPaymentState])

  const handleConfirmar = useCallback(() => {
    if (!selectedDireccionId) return
    checkoutMutation.mutate(
      {
        direccion_id: selectedDireccionId,
        forma_pago_codigo: selectedFormaPago,
        detalles: getItemsForCheckout(),
      },
      {
        onSuccess: (pedido) => {
          setCreatedPedido(pedido)
          if (selectedFormaPago === 'MERCADOPAGO') {
            setCheckoutPhase('tokenization')
          } else {
            setCheckoutPhase('result')
          }
        },
      }
    )
  }, [selectedDireccionId, selectedFormaPago, checkoutMutation, getItemsForCheckout])

  const handleApproved = useCallback((paymentId: number) => {
    setApproved(paymentId)
    setPaymentResult({ status: 'approved', paymentId })
    setCheckoutPhase('result')
  }, [setApproved])

  const handleRejected = useCallback((error: string) => {
    setRejected(error)
    setPaymentResult({ status: 'rejected', paymentId: null, error })
    setCheckoutPhase('result')
  }, [setRejected])

  const handlePending = useCallback((paymentId: number) => {
    setPaymentResult({ status: 'pending', paymentId })
    setCheckoutPhase('result')
  }, [])

  const handlePaymentCancel = useCallback(() => {
    setCheckoutPhase('form')
  }, [])

  const handleRetry = useCallback(() => {
    resetPaymentState()
    setPaymentResult(null)
    setRetryCount((c) => c + 1)
    setCheckoutPhase('tokenization')
  }, [resetPaymentState])

  if (isCartEmpty && checkoutPhase === 'form' && !createdPedido) {
    return (
      <div className="max-w-lg mx-auto py-12">
        <EmptyState
          title="Tu carrito está vacío"
          description="Agregá productos al carrito antes de confirmar un pedido"
          action={<Button onClick={() => navigate('/catalogo')}>Ver catálogo</Button>}
        />
      </div>
    )
  }

  if (checkoutPhase === 'result' && createdPedido) {
    return (
      <OrderConfirmation
        pedidoId={createdPedido.id}
        total={createdPedido.total}
        paymentStatus={paymentResult?.status}
        paymentId={paymentResult?.paymentId}
        onRetry={paymentResult?.status === 'rejected' ? handleRetry : undefined}
      />
    )
  }

  if (checkoutPhase === 'tokenization' && createdPedido) {
    return (
      <CardTokenizationForm
        key={retryCount}
        pedidoId={createdPedido.id}
        total={createdPedido.total}
        onApproved={handleApproved}
        onRejected={handleRejected}
        onPending={handlePending}
        onCancel={handlePaymentCancel}
      />
    )
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <CheckoutSummary />
        </div>

        <div className="space-y-6">
          <AddressSelector
            selectedId={selectedDireccionId}
            onSelect={(d) => setSelectedDireccionId(d.id)}
          />

          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <PaymentMethodSelector
              selected={selectedFormaPago}
              onSelect={setSelectedFormaPago}
            />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-gray-900">Total a pagar</span>
              <span className="text-2xl font-bold text-gray-900">{formatARS(totalPrice)}</span>
            </div>

            <Button
              variant="primary"
              size="lg"
              className="w-full"
              disabled={!selectedDireccionId || checkoutMutation.isPending || isOffline}
              onClick={handleConfirmar}
            >
              {isOffline
                ? 'Sin conexión'
                : checkoutMutation.isPending
                  ? 'Creando pedido...'
                  : 'Confirmar pedido'}
            </Button>

            {checkoutMutation.isError && (
              authStatus ? (
                <NoPermissionMessage status={authStatus} />
              ) : (
                <ErrorMessage
                  message={getErrorMessage(checkoutMutation.error)}
                  onRetry={() => checkoutMutation.reset()}
                />
              )
            )}

            {isOffline && <OfflineMessage />}
          </div>
        </div>
      </div>

      {checkoutMutation.isPending && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 flex flex-col items-center gap-4">
            <LoadingSpinner />
            <p className="text-gray-600">Creando tu pedido...</p>
          </div>
        </div>
      )}
    </div>
  )
}
