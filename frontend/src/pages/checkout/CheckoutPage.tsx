import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { useCheckout, CheckoutSummary, AddressSelector, OrderConfirmation } from '@/features/checkout'
import { Button } from '@/shared/components'
import { LoadingSpinner, EmptyState, ErrorMessage, OfflineMessage, NoPermissionMessage } from '@/shared/ui'
import { getAuthErrorStatus, getErrorMessage } from '@/shared/api'
import { useOffline } from '@/shared/lib/hooks'

const formatARS = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)

export function CheckoutPage() {
  const navigate = useNavigate()
  const isCartEmpty = useCartStore((s) => s.isCartEmpty)
  const totalPrice = useCartStore((s) => s.totalPrice)
  const getItemsForCheckout = useCartStore((s) => s.getItemsForCheckout)
  const isOffline = useOffline()

  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(null)
  const checkoutMutation = useCheckout()

  const authStatus = checkoutMutation.isError ? getAuthErrorStatus(checkoutMutation.error) : undefined

  if (isCartEmpty && !checkoutMutation.isSuccess) {
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

  if (checkoutMutation.isSuccess) {
    return (
      <OrderConfirmation
        pedidoId={checkoutMutation.data.id}
        total={checkoutMutation.data.total}
      />
    )
  }

  const handleConfirmar = () => {
    if (!selectedDireccionId) return
    checkoutMutation.mutate({
      direccion_id: selectedDireccionId,
      forma_pago_codigo: 'EFECTIVO',
      detalles: getItemsForCheckout(),
    })
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
