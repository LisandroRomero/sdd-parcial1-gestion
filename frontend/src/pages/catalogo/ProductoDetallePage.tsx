import { useParams, Link, useNavigate } from 'react-router-dom'
import { useProductoDetalle } from '@/features/catalogo'
import { AddToCartButton } from '@/features/carrito/components/AddToCartButton'
import { LoadingSpinner } from '@/shared/ui/LoadingSpinner'
import { EmptyState } from '@/shared/ui/EmptyState'

const formatARS = (precio: string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(
    parseFloat(precio)
  )

export function ProductoDetallePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const numericId = id ? parseInt(id, 10) : 0

  const { data, isLoading, isError } = useProductoDetalle(numericId)

  function handleBack() {
    // Go back in history if possible, otherwise go to catalog
    navigate(-1)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <EmptyState
        icon={<span className="text-5xl">😕</span>}
        title="Producto no encontrado"
        description="El producto que buscás no existe o fue removido."
        action={
          <Link
            to="/catalogo"
            className="text-amber-600 hover:text-amber-700 font-medium underline underline-offset-2"
          >
            Volver al catálogo
          </Link>
        }
      />
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Back link */}
      <button
        onClick={handleBack}
        className="inline-flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-700 font-medium mb-6 group"
      >
        <span className="group-hover:-translate-x-0.5 transition-transform">←</span>
        Volver al catálogo
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Image */}
        <div className="rounded-2xl overflow-hidden bg-amber-50 aspect-square flex items-center justify-center border border-amber-100">
          {data.imagen_url ? (
            <img
              src={data.imagen_url}
              alt={data.nombre}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-7xl">🍽️</span>
          )}
        </div>

        {/* Details */}
        <div className="flex flex-col gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">{data.nombre}</h1>
            <p className="text-3xl font-extrabold text-amber-600">{formatARS(data.precio_base)}</p>
          </div>

          {data.descripcion && (
            <p className="text-gray-600 leading-relaxed">{data.descripcion}</p>
          )}

          {/* Categories */}
          {data.categorias.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Categorías
              </p>
              <div className="flex flex-wrap gap-1.5">
                {data.categorias.map((cat) => (
                  <span
                    key={cat.id}
                    className="text-xs bg-orange-50 text-orange-700 border border-orange-200 px-2.5 py-1 rounded-full font-medium"
                  >
                    {cat.nombre}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Ingredients */}
          {data.ingredientes.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Ingredientes
              </p>
              <div className="flex flex-wrap gap-1.5">
                {data.ingredientes.map((ing) => (
                  <span
                    key={ing.ingrediente_id}
                    className={`text-xs px-2.5 py-1 rounded-full font-medium border ${
                      ing.es_alergeno
                        ? 'bg-amber-50 text-amber-800 border-amber-300'
                        : 'bg-gray-50 text-gray-700 border-gray-200'
                    }`}
                  >
                    {ing.nombre}
                    {ing.es_alergeno && (
                      <span className="ml-1 text-amber-500" title="Alérgeno">⚠</span>
                    )}
                  </span>
                ))}
              </div>
              {data.tiene_alergenos && (
                <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                  ⚠️ Este producto contiene ingredientes alérgenos. Consultá con el personal si tenés restricciones alimentarias.
                </p>
              )}
            </div>
          )}

          {/* Add to cart */}
          <div className="mt-auto pt-4">
            <AddToCartButton producto={data} />
          </div>
        </div>
      </div>
    </div>
  )
}
