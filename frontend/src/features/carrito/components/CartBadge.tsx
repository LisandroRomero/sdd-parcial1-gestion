import { useCartStore } from '@/shared/lib/stores/cart.store'
import { useUIStore } from '@/shared/lib/stores/ui.store'

export function CartBadge() {
  const totalItems = useCartStore((s) => s.totalItems)
  const openModal = useUIStore((s) => s.openModal)

  return (
    <button
      type="button"
      aria-label={`Abrir carrito${totalItems > 0 ? ` (${totalItems} ítems)` : ''}`}
      onClick={() => openModal('cart-drawer')}
      className="relative p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      {totalItems > 0 && (
        <span
          aria-hidden="true"
          className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-primary text-white text-[11px] font-bold rounded-full flex items-center justify-center leading-none"
        >
          {totalItems > 99 ? '99+' : totalItems}
        </span>
      )}
    </button>
  )
}
