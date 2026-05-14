import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { CartItemCard } from './CartItemCard'
import { CartSummary } from './CartSummary'

export function CartDrawer() {
  const navigate = useNavigate()
  const activeModal = useUIStore((s) => s.activeModal)
  const closeModal = useUIStore((s) => s.closeModal)
  const items = useCartStore((s) => s.items)
  const isCartEmpty = useCartStore((s) => s.isCartEmpty)

  const isOpen = activeModal === 'cart-drawer'

  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeModal()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, closeModal])

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black/40 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={closeModal}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Carrito de compras"
        className={`fixed top-0 right-0 h-full w-full max-w-sm bg-white shadow-2xl z-50 flex flex-col transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">Carrito de compras</h2>
          <button
            type="button"
            aria-label="Cerrar carrito"
            onClick={closeModal}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5">
          {isCartEmpty ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-8 w-8 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-gray-700 font-semibold">Tu carrito está vacío</p>
                <p className="text-sm text-gray-400 mt-1">Agregá productos del catálogo para empezar.</p>
              </div>
              <button
                type="button"
                onClick={() => {
                  closeModal()
                  navigate('/catalogo')
                }}
                className="text-sm font-medium text-primary hover:underline"
              >
                Ir al catálogo →
              </button>
            </div>
          ) : (
            <div>
              {items.map((item) => (
                <CartItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </div>

        {/* Footer with summary */}
        {!isCartEmpty && (
          <div className="px-5 pb-6 pt-2">
            <CartSummary />
          </div>
        )}
      </div>
    </>
  )
}
