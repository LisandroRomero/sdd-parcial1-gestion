import { useState } from 'react'
import { useListarCategoriasAdmin } from '@/features/admin/hooks/useListarCategoriasAdmin'
import { useCrearCategoria } from '@/features/admin/hooks/useCrearCategoria'
import { useActualizarCategoria } from '@/features/admin/hooks/useActualizarCategoria'
import { useEliminarCategoria } from '@/features/admin/hooks/useEliminarCategoria'
import type { CategoriaAdminRead, CategoriaCreate, CategoriaUpdate } from '@/entities/admin/types'
import { LoadingSpinner, ErrorMessage, EmptyState, OfflineMessage, NoPermissionMessage } from '@/shared/ui'
import { Button } from '@/shared/components'
import { useOffline } from '@/shared/lib/hooks'
import { getAuthErrorStatus, getErrorMessage } from '@/shared/api'

// ---------------------------------------------------------------------------
// Modal — Crear / Editar categoria
// ---------------------------------------------------------------------------
interface CategoriaModalProps {
  initial?: CategoriaAdminRead
  categorias: CategoriaAdminRead[]
  onClose: () => void
  onSave: (body: CategoriaCreate | CategoriaUpdate) => void
  isLoading: boolean
  error?: string | null
}

function CategoriaModal({
  initial,
  categorias,
  onClose,
  onSave,
  isLoading,
  error,
}: CategoriaModalProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? '')
  const [descripcion, setDescripcion] = useState(initial?.descripcion ?? '')
  const [parentId, setParentId] = useState<string>(
    initial?.parent_id != null ? String(initial.parent_id) : '',
  )

  // Exclude the current category from parent options to avoid circular refs
  const parentOptions = categorias.filter((c) => c.id !== initial?.id)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const body: CategoriaCreate = {
      nombre,
      descripcion: descripcion || undefined,
      parent_id: parentId ? parseInt(parentId, 10) : undefined,
    }
    onSave(body)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold text-gray-900 mb-4">
          {initial ? `Editar categoria #${initial.id}` : 'Nueva categoria'}
        </h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoria padre
            </label>
            <select
              value={parentId}
              onChange={(e) => setParentId(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
            >
              <option value="">Sin categoria padre</option>
              {parentOptions.map((cat) => (
                <option key={cat.id} value={String(cat.id)}>
                  {cat.nombre}
                </option>
              ))}
            </select>
          </div>

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
// Main page
// ---------------------------------------------------------------------------
export function AdminCategoriasPage() {
  const [showCreate, setShowCreate] = useState(false)
  const [editingCategoria, setEditingCategoria] = useState<CategoriaAdminRead | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
  const [mutationError, setMutationError] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const isOffline = useOffline()

  const { data, isLoading, isError, error, refetch } = useListarCategoriasAdmin()
  const crearCategoria = useCrearCategoria()
  const actualizarCategoria = useActualizarCategoria()
  const eliminarCategoria = useEliminarCategoria()

  const categorias = data ?? []

  // Build an id -> nombre map for parent lookups
  const categoriaMap = new Map(categorias.map((c) => [c.id, c.nombre]))

  function handleCreate(body: CategoriaCreate | CategoriaUpdate) {
    setMutationError(null)
    crearCategoria.mutate(body as CategoriaCreate, {
      onSuccess: () => setShowCreate(false),
      onError: (err) => {
        setMutationError(getErrorMessage(err))
      },
    })
  }

  function handleUpdate(body: CategoriaCreate | CategoriaUpdate) {
    if (!editingCategoria) return
    setMutationError(null)
    actualizarCategoria.mutate(
      { id: editingCategoria.id, body: body as CategoriaUpdate },
      {
        onSuccess: () => setEditingCategoria(null),
        onError: (err) => {
          setMutationError(getErrorMessage(err))
        },
      },
    )
  }

  function handleDelete(id: number) {
    setDeleteError(null)
    eliminarCategoria.mutate(id, {
      onSuccess: () => setConfirmDeleteId(null),
      onError: (err) => {
        setDeleteError(getErrorMessage(err))
      },
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
      getAuthErrorStatus(error) ? (
        <NoPermissionMessage status={getAuthErrorStatus(error)} />
      ) : (
        <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
      )
    )
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gestion de categorias</h1>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setMutationError(null)
            setShowCreate(true)
          }}
        >
          + Nueva categoria
        </Button>
      </div>

      {isOffline && <div className="mb-4"><OfflineMessage /></div>}

      {categorias.length === 0 ? (
        <EmptyState
          title="No hay categorias"
          description="Crea la primera categoria usando el boton de arriba."
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
                  Descripcion
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Categoria padre
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {categorias.map((cat) => (
                <tr key={cat.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{cat.nombre}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                    {cat.descripcion ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {cat.parent_id != null
                      ? (categoriaMap.get(cat.parent_id) ?? `#${cat.parent_id}`)
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {cat.created_at
                      ? new Date(cat.created_at).toLocaleDateString('es-AR')
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setMutationError(null)
                          setEditingCategoria(cat)
                        }}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setDeleteError(null)
                          setConfirmDeleteId(cat.id)
                        }}
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
        <CategoriaModal
          categorias={categorias}
          onClose={() => setShowCreate(false)}
          onSave={handleCreate}
          isLoading={crearCategoria.isPending}
          error={mutationError}
        />
      )}

      {editingCategoria && (
        <CategoriaModal
          initial={editingCategoria}
          categorias={categorias}
          onClose={() => setEditingCategoria(null)}
          onSave={handleUpdate}
          isLoading={actualizarCategoria.isPending}
          error={mutationError}
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
            <h2 className="text-lg font-bold text-gray-900 mb-2">Eliminar categoria</h2>
            <p className="text-sm text-gray-600 mb-2">
              Esta accion eliminara la categoria. Si tiene productos o subcategorias asociadas la
              operacion fallara.
            </p>
            {deleteError && (
              <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
                {deleteError}
              </div>
            )}
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="ghost" size="sm" onClick={() => setConfirmDeleteId(null)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={eliminarCategoria.isPending}
                onClick={() => handleDelete(confirmDeleteId)}
                className="bg-red-600 hover:bg-red-700 border-red-600"
              >
                {eliminarCategoria.isPending ? 'Eliminando…' : 'Confirmar'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
