import { useState } from 'react'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { Button } from '@/shared/components'

const formatARS = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)

export function CartSummary() {
  const totalItems = useCartStore((s) => s.totalItems)
  const totalPrice = useCartStore((s) => s.totalPrice)
  const isCartEmpty = useCartStore((s) => s.isCartEmpty)
  const clearCart = useCartStore((s) => s.clearCart)

  const [confirmingClear, setConfirmingClear] = useState(false)

  const handleClearCart = () => {
    if (!confirmingClear) {
      setConfirmingClear(true)
      return
    }
    clearCart()
    setConfirmingClear(false)
  }

  const handleCancelClear = () => {
    setConfirmingClear(false)
  }

  return (
    <div className="border-t border-gray-200 pt-4 space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Productos</span>
          <span>{totalItems} {totalItems === 1 ? 'ítem' : 'ítems'}</span>
        </div>
        <div className="flex justify-between text-base font-bold text-gray-900">
          <span>Total</span>
          <span>{formatARS(totalPrice)}</span>
        </div>
      </div>

      <Button
        variant="primary"
        className="w-full"
        disabled={isCartEmpty}
        onClick={() => {
          // TODO Epic 5: navigate to checkout route
        }}
      >
        Confirmar pedido
      </Button>

      {!isCartEmpty && (
        <div className="flex items-center gap-2">
          {confirmingClear ? (
            <>
              <Button variant="outline" size="sm" onClick={handleCancelClear} className="flex-1">
                Cancelar
              </Button>
              <Button variant="secondary" size="sm" onClick={handleClearCart} className="flex-1">
                Sí, vaciar
              </Button>
            </>
          ) : (
            <button
              type="button"
              onClick={handleClearCart}
              className="w-full text-sm text-gray-400 hover:text-red-500 transition-colors py-1"
            >
              Vaciar carrito
            </button>
          )}
        </div>
      )}
    </div>
  )
}
