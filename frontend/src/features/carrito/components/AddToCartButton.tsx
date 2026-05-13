import { useState } from 'react'
import type { ProductoDetalleRead } from '@/entities/producto'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { Button } from '@/shared/components'
import { IngredientToggle } from './IngredientToggle'

interface AddToCartButtonProps {
  producto: ProductoDetalleRead
}

export function AddToCartButton({ producto }: AddToCartButtonProps) {
  const addItem = useCartStore((s) => s.addItem)
  const showToast = useUIStore((s) => s.showToast)

  const removiblesIngredients = producto.ingredientes.filter((i) => i.es_removible)
  const hasRemovibles = removiblesIngredients.length > 0

  // Track which removible ingredients are INCLUDED (checked = included, unchecked = excluded)
  const [included, setIncluded] = useState<Set<number>>(
    () => new Set(removiblesIngredients.map((i) => i.ingrediente_id)),
  )
  const [showCustomization, setShowCustomization] = useState(false)

  if (!producto.disponible) {
    return (
      <Button variant="secondary" disabled className="w-full opacity-60 cursor-not-allowed">
        No disponible
      </Button>
    )
  }

  const handleDirectAdd = () => {
    addItem(
      {
        id: producto.id,
        nombre: producto.nombre,
        precio_base: producto.precio_base,
        imagenUrl: producto.imagen_url ?? undefined,
      },
      1,
    )
    showToast('Producto agregado al carrito', 'success')
  }

  const handleConfirmCustomization = () => {
    const ingredientesExcluidos = removiblesIngredients
      .filter((i) => !included.has(i.ingrediente_id))
      .map((i) => i.ingrediente_id)

    addItem(
      {
        id: producto.id,
        nombre: producto.nombre,
        precio_base: producto.precio_base,
        imagenUrl: producto.imagen_url ?? undefined,
      },
      1,
      { ingredientesExcluidos },
    )
    showToast('Producto agregado al carrito', 'success')
    setShowCustomization(false)
  }

  const toggleIncluded = (ingredienteId: number) => {
    setIncluded((prev) => {
      const next = new Set(prev)
      if (next.has(ingredienteId)) {
        next.delete(ingredienteId)
      } else {
        next.add(ingredienteId)
      }
      return next
    })
  }

  if (!hasRemovibles) {
    return (
      <Button variant="primary" onClick={handleDirectAdd} className="w-full">
        Agregar al carrito
      </Button>
    )
  }

  return (
    <div>
      {!showCustomization ? (
        <Button variant="primary" onClick={() => setShowCustomization(true)} className="w-full">
          Agregar al carrito
        </Button>
      ) : (
        <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 space-y-3">
          <p className="text-sm font-semibold text-gray-800">Personalizar ingredientes</p>
          <p className="text-xs text-gray-500">Destildá los ingredientes que no querés incluir.</p>
          <div className="space-y-0.5">
            {removiblesIngredients.map((ing) => (
              <IngredientToggle
                key={ing.ingrediente_id}
                ingrediente={ing}
                checked={included.has(ing.ingrediente_id)}
                onChange={() => toggleIncluded(ing.ingrediente_id)}
              />
            ))}
          </div>
          <div className="flex gap-2 pt-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCustomization(false)}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleConfirmCustomization}
              className="flex-1"
            >
              Agregar
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
