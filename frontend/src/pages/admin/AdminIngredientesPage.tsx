import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useCrearIngrediente } from '@/features/admin/hooks/useCrearIngrediente'
import { listarIngredientesAdmin } from '@/features/admin/api/adminIngredientesApi'
import { useActualizarIngrediente } from '@/features/admin/hooks/useActualizarIngrediente'
import { useEliminarIngrediente } from '@/features/admin/hooks/useEliminarIngrediente'
import type { IngredienteAdminRead, IngredienteCreate, IngredienteUpdate } from '@/entities/admin/types'
import { LoadingSpinner, ErrorMessage, EmptyState } from '@/shared/ui'
import { Button } from '@/shared/components'

// ---------------------------------------------------------------------------
// Badge
// ---------------------------------------------------------------------------
function AlergenoBadge({ esAlergeno }: { esAlergeno: boolean }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
        esAlergeno ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'
      }`}
    >
      {esAlergeno ? 'Alergeno' : 'No alergeno'}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Modal — Crear / Editar ingrediente
// ---------------------------------------------------------------------------
interface IngredienteModalProps {
  initial?: IngredienteAdminRead
  onClose: () => void
  onSave: (body: IngredienteCreate | IngredienteUpdate) => void
  isLoading: boolean
  error?: string | null
}

function IngredienteModal({
  initial,
  onClose,
  onSave,
  isLoading,
  error,
}: IngredienteModalProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? '')
  const [esAlergeno, setEsAlergeno] = useState(initial?.es_alergeno ?? false)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const body: IngredienteCreate = { nombre, es_alergeno: esAlergeno }
    onSave(body)
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
          {initial ? `Editar ingrediente #${initial.id}` : 'Nuevo ingrediente'}
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

          <div className="flex items-center gap-2">
            <input
              id="es-alergeno"
              type="checkbox"
              checked={esAlergeno}
              onChange={(e) => setEsAlergeno(e.target.checked)}
              className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
            />
            <label htmlFor="es-alergeno" className="text-sm font-medium text-gray-700">
              Es alergeno
            </label>
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
export function AdminIngredientesPage() {
  const [showCreate, setShowCreate] = useState(false)
  const [editingIngrediente, setEditingIngrediente] = useState<IngredienteAdminRead | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
  const [mutationError, setMutationError] = useState<string | null>(null)
  const [includeDeleted, setIncludeDeleted] = useState(false)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['admin-ingredientes', includeDeleted],
    queryFn: () => listarIngredientesAdmin(1, 100, includeDeleted),
  })
  const crearIngrediente = useCrearIngrediente()
  const actualizarIngrediente = useActualizarIngrediente()
  const eliminarIngrediente = useEliminarIngrediente()

  const ingredientes = data?.items ?? []

  function handleCreate(body: IngredienteCreate | IngredienteUpdate) {
    setMutationError(null)
    crearIngrediente.mutate(body as IngredienteCreate, {
      onSuccess: () => setShowCreate(false),
      onError: (err) => {
        const msg = err instanceof Error ? err.message : 'Error al crear el ingrediente'
        setMutationError(msg)
      },
    })
  }

  function handleUpdate(body: IngredienteCreate | IngredienteUpdate) {
    if (!editingIngrediente) return
    setMutationError(null)
    actualizarIngrediente.mutate(
      { id: editingIngrediente.id, body: body as IngredienteUpdate },
      {
        onSuccess: () => setEditingIngrediente(null),
        onError: (err) => {
          const msg = err instanceof Error ? err.message : 'Error al actualizar el ingrediente'
          setMutationError(msg)
        },
      },
    )
  }

  function handleDelete(id: number) {
    eliminarIngrediente.mutate(id, {
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
        message={error instanceof Error ? error.message : 'Error al cargar los ingredientes'}
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gestion de ingredientes</h1>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setMutationError(null)
            setShowCreate(true)
          }}
        >
          + Nuevo ingrediente
        </Button>
      </div>

      <div className="mb-4">
        <label className="inline-flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={includeDeleted}
            onChange={(e) => setIncludeDeleted(e.target.checked)}
            className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
          />
          <span className="text-sm text-gray-700 font-medium">Mostrar eliminados</span>
        </label>
      </div>

      {ingredientes.length === 0 ? (
        <EmptyState
          title="No hay ingredientes"
          description="Crea el primer ingrediente usando el boton de arriba."
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
                  Alergeno
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
              {ingredientes.map((ing) => (
                <tr key={ing.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">{ing.nombre}</span>
                      {ing.deleted_at && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
                          Eliminado
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <AlergenoBadge esAlergeno={ing.es_alergeno} />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {ing.created_at
                      ? new Date(ing.created_at).toLocaleDateString('es-AR')
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setMutationError(null)
                          setEditingIngrediente(ing)
                        }}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setConfirmDeleteId(ing.id)}
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
        <IngredienteModal
          onClose={() => setShowCreate(false)}
          onSave={handleCreate}
          isLoading={crearIngrediente.isPending}
          error={mutationError}
        />
      )}

      {editingIngrediente && (
        <IngredienteModal
          initial={editingIngrediente}
          onClose={() => setEditingIngrediente(null)}
          onSave={handleUpdate}
          isLoading={actualizarIngrediente.isPending}
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
            <h2 className="text-lg font-bold text-gray-900 mb-2">Eliminar ingrediente</h2>
            <p className="text-sm text-gray-600 mb-6">
              Esta accion eliminara el ingrediente. Si esta asociado a productos, la operacion
              puede fallar.
            </p>
            <div className="flex justify-end gap-3">
              <Button variant="ghost" size="sm" onClick={() => setConfirmDeleteId(null)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={eliminarIngrediente.isPending}
                onClick={() => handleDelete(confirmDeleteId)}
                className="bg-red-600 hover:bg-red-700 border-red-600"
              >
                {eliminarIngrediente.isPending ? 'Eliminando…' : 'Confirmar'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
