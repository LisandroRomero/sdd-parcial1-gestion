import { useCartStore } from '@/shared/lib/stores/cart.store'
import { Card, CardHeader, CardContent } from '@/shared/components'

const formatARS = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value)

export function CheckoutSummary() {
  const items = useCartStore((s) => s.items)
  const totalItems = useCartStore((s) => s.totalItems)
  const totalPrice = useCartStore((s) => s.totalPrice)

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">Resumen del pedido</h3>
        <p className="text-sm text-gray-500">{totalItems} {totalItems === 1 ? 'producto' : 'productos'}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id} className="flex justify-between items-start pb-4 border-b border-gray-100 last:border-0">
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.nombre}</p>
                <p className="text-sm text-gray-500">Cantidad: {item.cantidad}</p>
                {item.ingredientesExcluidos.length > 0 && (
                  <p className="text-xs text-gray-400">Sin ingredientes extra</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">{formatARS(parseFloat(item.precio_base) * item.cantidad)}</p>
                <p className="text-xs text-gray-400">{formatARS(parseFloat(item.precio_base))} c/u</p>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 pt-4 border-t border-gray-200 flex justify-between items-center">
          <span className="text-base font-semibold text-gray-900">Total</span>
          <span className="text-xl font-bold text-gray-900">{formatARS(totalPrice)}</span>
        </div>
      </CardContent>
    </Card>
  )
}
