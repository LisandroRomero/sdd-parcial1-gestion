import { useState } from 'react'
import { useProductos } from '@/features/catalogo/hooks/useProductos'
import { useCrearProducto } from '@/features/admin/hooks/useCrearProducto'
import { useActualizarProducto } from '@/features/admin/hooks/useActualizarProducto'
import { useEliminarProducto } from '@/features/admin/hooks/useEliminarProducto'
import { useActualizarStock } from '@/features/admin/hooks/useActualizarStock'
import { useCambiarDisponibilidadAdmin } from '@/features/admin/hooks/useCambiarDisponibilidadAdmin'
import { useListarCategoriasAdmin } from '@/features/admin/hooks/useListarCategoriasAdmin'
import type { ProductoRead, ProductoCreate, ProductoUpdate } from '@/entities/producto/types'
import { LoadingSpinner, ErrorMessage, EmptyState } from '@/shared/ui'
import { Button } from '@/shared/components'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatPrecio(precio: string) {
  return `$${parseFloat(precio).toLocaleString('es-AR', { minimumFractionDigits: 2 })}`
}

// ---------------------------------------------------------------------------
// Badges
// ---------------------------------------------------------------------------
function DisponibleBadge({ disponible }: { disponible: boolean }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
        disponible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}
    >
      {disponible ? 'Disponible' : 'No disponible'}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Modal — Crear / Editar producto
// ---------------------------------------------------------------------------
interface ProductoModalProps {
  initial?: ProductoRead
  categorias: { id: number; nombre: string }[]
  onClose: () => void
  onSave: (body: ProductoCreate | ProductoUpdate) => void
  isLoading: boolean
  error?: string | null
}

function ProductoModal({
  initial,
  categorias,
  onClose,
  onSave,
  isLoading,
  error,
}: ProductoModalProps) {
  const [sku, setSku] = useState(initial?.codigo_sku ?? '')
  const [nombre, setNombre] = useState(initial?.nombre ?? '')
  const [descripcion, setDescripcion] = useState(initial?.descripcion ?? '')
  const [precio, setPrecio] = useState(initial?.precio_base ?? '')
  const [stock, setStock] = useState(String(initial?.stock_cantidad ?? 0))
  const [disponible, setDisponible] = useState(initial?.disponible ?? true)
  const [imagenUrl, setImagenUrl] = useState(initial?.imagen_url ?? '')
  const [selectedCategorias, setSelectedCategorias] = useState<number[]>([])

  function toggleCategoria(id: number) {
    setSelectedCategorias((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id],
    )
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const body: ProductoCreate = {
      codigo_sku: sku,
      nombre,
      descripcion: descripcion || undefined,
      precio_base: precio,
      stock_cantidad: parseInt(stock, 10),
      disponible,
      imagen_url: imagenUrl || undefined,
      categoria_ids: selectedCategorias,
    }
    onSave(body)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold text-gray-900 mb-4">
          {initial ? `Editar producto #${initial.id}` : 'Nuevo producto'}
        </h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SKU *</label>
              <input
                type="text"
                required
                value={sku}
                onChange={(e) => setSku(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Precio base *</label>
              <input
                type="number"
                required
                step="0.01"
                min="0"
                value={precio}
                onChange={(e) => setPrecio(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input
              type="text"
              required
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Descripcion</label>
            <textarea
              rows={2}
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock *</label>
              <input
                type="number"
                required
                min="0"
                value={stock}
                onChange={(e) => setStock(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">URL imagen</label>
              <input
                type="url"
                value={imagenUrl}
                onChange={(e) => setImagenUrl(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              id="disponible"
              type="checkbox"
              checked={disponible}
              onChange={(e) => setDisponible(e.target.checked)}
              className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
            />
            <label htmlFor="disponible" className="text-sm font-medium text-gray-700">
              Disponible para venta
            </label>
          </div>

          {categorias.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categorias</label>
              <div className="flex flex-wrap gap-2 max-h-28 overflow-y-auto">
                {categorias.map((cat) => (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => toggleCategoria(cat.id)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium border transition-colors ${
                      selectedCategorias.includes(cat.id)
                        ? 'bg-primary text-white border-primary'
                        : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {cat.nombre}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={isLoading}>
              {isLoading ? 'Guardando…' : 'Guardar'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Modal — Actualizar stock
// ---------------------------------------------------------------------------
interface StockModalProps {
  producto: ProductoRead
  onClose: () => void
  onSave: (cantidad: number) => void
  isLoading: boolean
}

function StockModal({ producto, onClose, onSave, isLoading }: StockModalProps) {
  const [cantidad, setCantidad] = useState(String(producto.stock_cantidad))

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onSave(parseInt(cantidad, 10))
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold text-gray-900 mb-4">
          Actualizar stock — {producto.nombre}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nueva cantidad
            </label>
            <input
              type="number"
              required
              min="0"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={isLoading}>
              {isLoading ? 'Guardando…' : 'Guardar'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export function AdminProductosPage() {
  const [showCreate, setShowCreate] = useState(false)
  const [editingProducto, setEditingProducto] = useState<ProductoRead | null>(null)
  const [stockProducto, setStockProducto] = useState<ProductoRead | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
  const [mutationError, setMutationError] = useState<string | null>(null)

  const { data, isLoading, isError, error, refetch } = useProductos({})
  const categoriasQuery = useListarCategoriasAdmin()

  const crearProducto = useCrearProducto()
  const actualizarProducto = useActualizarProducto()
  const eliminarProducto = useEliminarProducto()
  const actualizarStock = useActualizarStock()
  const cambiarDisponibilidad = useCambiarDisponibilidadAdmin()

  const productos = data?.items ?? []
  const categorias = categoriasQuery.data?.items ?? []

  function handleCreate(body: ProductoCreate | ProductoUpdate) {
    setMutationError(null)
    crearProducto.mutate(body as ProductoCreate, {
      onSuccess: () => setShowCreate(false),
      onError: (err) => {
        const msg = err instanceof Error ? err.message : 'Error al crear el producto'
        setMutationError(msg)
      },
    })
  }

  function handleUpdate(body: ProductoCreate | ProductoUpdate) {
    if (!editingProducto) return
    setMutationError(null)
    actualizarProducto.mutate(
      { id: editingProducto.id, body: body as ProductoUpdate },
      {
        onSuccess: () => setEditingProducto(null),
        onError: (err) => {
          const msg = err instanceof Error ? err.message : 'Error al actualizar el producto'
          setMutationError(msg)
        },
      },
    )
  }

  function handleToggleDisponible(producto: ProductoRead) {
    cambiarDisponibilidad.mutate({
      id: producto.id,
      body: { disponible: !producto.disponible },
    })
  }

  function handleStockSave(cantidad: number) {
    if (!stockProducto) return
    actualizarStock.mutate(
      { id: stockProducto.id, body: { stock_cantidad: cantidad } },
      { onSuccess: () => setStockProducto(null) },
    )
  }

  function handleDelete(id: number) {
    eliminarProducto.mutate(id, {
      onSuccess: () => setConfirmDeleteId(null),
    })
  }

  if (isLoading && !data) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner />
      </div>
    )
  }

  if (isError && !data) {
    return (
      <ErrorMessage
        message={error instanceof Error ? error.message : 'Error al cargar los productos'}
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gestion de productos</h1>
        <Button variant="primary" size="sm" onClick={() => { setMutationError(null); setShowCreate(true) }}>
          + Nuevo producto
        </Button>
      </div>

      {productos.length === 0 ? (
        <EmptyState
          title="No hay productos"
          description="Crea el primer producto usando el boton de arriba."
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {productos.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-gray-900">{p.nombre}</span>
                    {p.descripcion && (
                      <p className="text-xs text-gray-500 truncate max-w-xs">{p.descripcion}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 font-mono">{p.codigo_sku}</td>
                  <td className="px-4 py-3 text-sm text-gray-900 font-medium">
                    {formatPrecio(p.precio_base)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.stock_cantidad}</td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => handleToggleDisponible(p)}
                      disabled={cambiarDisponibilidad.isPending}
                      className="focus:outline-none"
                      title="Click para cambiar disponibilidad"
                    >
                      <DisponibleBadge disponible={p.disponible} />
                    </button>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => { setMutationError(null); setEditingProducto(p) }}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setStockProducto(p)}
                      >
                        Stock
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setConfirmDeleteId(p.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Eliminar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modals */}
      {showCreate && (
        <ProductoModal
          categorias={categorias}
          onClose={() => setShowCreate(false)}
          onSave={handleCreate}
          isLoading={crearProducto.isPending}
          error={mutationError}
        />
      )}

      {editingProducto && (
        <ProductoModal
          initial={editingProducto}
          categorias={categorias}
          onClose={() => setEditingProducto(null)}
          onSave={handleUpdate}
          isLoading={actualizarProducto.isPending}
          error={mutationError}
        />
      )}

      {stockProducto && (
        <StockModal
          producto={stockProducto}
          onClose={() => setStockProducto(null)}
          onSave={handleStockSave}
          isLoading={actualizarStock.isPending}
        />
      )}

      {/* Confirm delete dialog */}
      {confirmDeleteId !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setConfirmDeleteId(null)}
        >
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-bold text-gray-900 mb-2">Eliminar producto</h2>
            <p className="text-sm text-gray-600 mb-6">
              Esta accion eliminara el producto de forma logica. El historial de pedidos se mantiene.
            </p>
            <div className="flex justify-end gap-3">
              <Button variant="ghost" size="sm" onClick={() => setConfirmDeleteId(null)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={eliminarProducto.isPending}
                onClick={() => handleDelete(confirmDeleteId)}
                className="bg-red-600 hover:bg-red-700 border-red-600"
              >
                {eliminarProducto.isPending ? 'Eliminando…' : 'Confirmar'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
