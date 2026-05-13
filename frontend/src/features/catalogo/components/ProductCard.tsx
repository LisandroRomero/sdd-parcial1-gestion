import { Link } from 'react-router-dom'
import type { ProductoRead } from '@/entities/producto'

interface ProductCardProps {
  producto: ProductoRead
}

const formatARS = (precio: string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(
    parseFloat(precio)
  )

export function ProductCard({ producto }: ProductCardProps) {
  return (
    <Link
      to={`/catalogo/${producto.id}`}
      className="group block bg-white rounded-2xl shadow-sm border border-amber-100 overflow-hidden hover:-translate-y-1 transition-transform duration-200 hover:shadow-md"
    >
      <div className="aspect-video w-full overflow-hidden bg-amber-50">
        {producto.imagen_url ? (
          <img
            src={producto.imagen_url}
            alt={producto.nombre}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-4xl">🍽️</span>
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-2 mb-2">
          {producto.nombre}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-amber-600 font-bold text-base">
            {formatARS(producto.precio_base)}
          </span>
          {!producto.disponible && (
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
              No disponible
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}
