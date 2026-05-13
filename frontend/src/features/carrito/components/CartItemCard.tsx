import type { CartItem } from '@/shared/lib/stores/cart.store'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { QuantityControl } from '@/shared/components'

interface CartItemCardProps {
  item: CartItem
}

const formatARS = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)

export function CartItemCard({ item }: CartItemCardProps) {
  const updateQuantity = useCartStore((s) => s.updateQuantity)
  const removeItem = useCartStore((s) => s.removeItem)

  const unitPrice = parseFloat(item.precio_base)
  const subtotal = unitPrice * item.cantidad

  return (
    <div className="flex flex-col gap-2 py-4 border-b border-gray-100 last:border-0">
      <div className="flex items-start justify-between gap-3">
        {item.imagenUrl && (
          <img
            src={item.imagenUrl}
            alt={item.nombre}
            className="w-14 h-14 rounded-lg object-cover flex-shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">{item.nombre}</p>
          <p className="text-xs text-gray-500 mt-0.5">{formatARS(unitPrice)} c/u</p>
        </div>
        <button
          type="button"
          aria-label={`Eliminar ${item.nombre} del carrito`}
          onClick={() => removeItem(item.id)}
          className="text-gray-400 hover:text-red-500 transition-colors flex-shrink-0 p-1 rounded"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex items-center justify-between">
        <QuantityControl
          value={item.cantidad}
          onChange={(v) => updateQuantity(item.id, v)}
          min={1}
        />
        <p className="text-sm font-semibold text-gray-900">{formatARS(subtotal)}</p>
      </div>

      {item.ingredientesExcluidos.length > 0 && (
        <p className="text-xs text-gray-400 italic">
          Sin:{' '}
          {item.ingredientesExcluidos
            .map((id) => `ing. #${id}`)
            .join(', ')}
        </p>
      )}
    </div>
  )
}
