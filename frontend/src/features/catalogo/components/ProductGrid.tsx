import type { ProductoRead } from '@/entities/producto'
import { EmptyState } from '@/shared/ui/EmptyState'
import { ProductCard } from './ProductCard'
import { ProductCardSkeleton } from './ProductCardSkeleton'

interface ProductGridProps {
  items: ProductoRead[]
  isLoading: boolean
}

export function ProductGrid({ items, isLoading }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <EmptyState
        icon={<span className="text-5xl">🔍</span>}
        title="No se encontraron productos"
        description="Intentá con otros filtros o limpiá la búsqueda para ver todos los productos."
      />
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {items.map((producto) => (
        <ProductCard key={producto.id} producto={producto} />
      ))}
    </div>
  )
}
