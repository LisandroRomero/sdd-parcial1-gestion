import { useState, useCallback } from 'react'
import { useListarUsuariosAdmin } from '@/features/admin/hooks/useListarUsuariosAdmin'
import { useToggleEstadoUsuario } from '@/features/admin/hooks/useToggleEstadoUsuario'
import { useActualizarUsuarioAdmin } from '@/features/admin/hooks/useActualizarUsuarioAdmin'
import type { AdminUsuarioRead, AdminUsuarioUpdate } from '@/entities/admin/types'
import { OrderPagination } from '@/features/pedidos/components/OrderPagination'
import { LoadingSpinner, ErrorMessage, EmptyState, NoPermissionMessage, OfflineMessage } from '@/shared/ui'
import { Button } from '@/shared/components'
import { getAuthErrorStatus, getErrorMessage } from '@/shared/api'
import { useOffline } from '@/shared/lib/hooks'

const ROLES = ['CLIENT', 'ADMIN', 'GESTOR_PEDIDOS', 'GESTOR_STOCK'] as const

// ---------------------------------------------------------------------------
// Debounce hook
// ---------------------------------------------------------------------------
function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  const timerRef = { current: 0 as ReturnType<typeof setTimeout> }

  const memoized = useCallback(
    (newValue: T) => {
      clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => setDebounced(newValue), delay)
    },
    [delay],
  )

  void memoized // mark as used
  return debounced
}

// ---------------------------------------------------------------------------
// Role badge
// ---------------------------------------------------------------------------
const ROLE_COLORS: Record<string, string> = {
  ADMIN: 'bg-red-100 text-red-700',
  CLIENT: 'bg-blue-100 text-blue-700',
  GESTOR_PEDIDOS: 'bg-purple-100 text-purple-700',
  GESTOR_STOCK: 'bg-yellow-100 text-yellow-700',
}

function RoleBadge({ rol }: { rol: string }) {
  const color = ROLE_COLORS[rol] ?? 'bg-gray-100 text-gray-700'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {rol}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Edit modal
// ---------------------------------------------------------------------------
interface EditModalProps {
  usuario: AdminUsuarioRead
  onClose: () => void
  onSave: (body: AdminUsuarioUpdate) => void
  isLoading: boolean
}

function EditModal({ usuario, onClose, onSave, isLoading }: EditModalProps) {
  const [nombre, setNombre] = useState(usuario.nombre ?? '')
  const [apellido, setApellido] = useState(usuario.apellido ?? '')
  const [email, setEmail] = useState(usuario.email)
  const [selectedRoles, setSelectedRoles] = useState<string[]>([...usuario.roles])

  function toggleRole(rol: string) {
    setSelectedRoles((prev) =>
      prev.includes(rol) ? prev.filter((r) => r !== rol) : [...prev, rol],
    )
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const body: AdminUsuarioUpdate = {}
    if (nombre !== (usuario.nombre ?? '')) body.nombre = nombre
    if (apellido !== (usuario.apellido ?? '')) body.apellido = apellido
    if (email !== usuario.email) body.email = email

    // Always send roles to allow role changes
    const rolesChanged =
      selectedRoles.length !== usuario.roles.length ||
      selectedRoles.some((r) => !usuario.roles.includes(r))
    if (rolesChanged) body.roles = selectedRoles

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
          Editar usuario #{usuario.id}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
            <input
              type="text"
              value={apellido}
              onChange={(e) => setApellido(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Roles</label>
            <div className="flex flex-wrap gap-2">
              {ROLES.map((rol) => (
                <button
                  key={rol}
                  type="button"
                  onClick={() => toggleRole(rol)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                    selectedRoles.includes(rol)
                      ? 'bg-primary text-white border-primary'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {rol}
                </button>
              ))}
            </div>
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
export function AdminUsuariosPage() {
  const [buscarInput, setBuscarInput] = useState('')
  const [buscar, setBuscar] = useState<string | undefined>(undefined)
  const [rol, setRol] = useState<string | undefined>(undefined)
  const [page, setPage] = useState(1)
  const [editingUser, setEditingUser] = useState<AdminUsuarioRead | null>(null)
  const isOffline = useOffline()

  const { data, isLoading, isError, error, refetch } = useListarUsuariosAdmin({
    buscar: buscar || undefined,
    rol: rol || undefined,
    page,
    size: 20,
  })

  const toggleEstado = useToggleEstadoUsuario()
  const actualizarUsuario = useActualizarUsuarioAdmin()
  const authStatus = isError ? getAuthErrorStatus(error) : undefined

  // Debounce search — trigger query update after 400ms
  let debounceTimer: ReturnType<typeof setTimeout>
  function handleBuscarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    setBuscarInput(value)
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      setBuscar(value || undefined)
      setPage(1)
    }, 400)
  }

  function handleRolChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setRol(e.target.value || undefined)
    setPage(1)
  }

  function handleToggleEstado(usuario: AdminUsuarioRead) {
    toggleEstado.mutate({ id: usuario.id, body: { activo: !usuario.activo } })
  }

  function handleSaveEdit(body: AdminUsuarioUpdate) {
    if (!editingUser) return
    actualizarUsuario.mutate(
      { id: editingUser.id, body },
      { onSuccess: () => setEditingUser(null) },
    )
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
      authStatus ? (
        <NoPermissionMessage status={authStatus} />
      ) : (
        <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
      )
    )
  }

  const usuarios = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 0

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Gestión de usuarios</h1>
      {isOffline && <div className="mb-4"><OfflineMessage /></div>}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <input
          type="text"
          placeholder="Buscar por nombre o email…"
          value={buscarInput}
          onChange={handleBuscarChange}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <select
          value={rol ?? ''}
          onChange={handleRolChange}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
        >
          <option value="">Todos los roles</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      {usuarios.length === 0 ? (
        <EmptyState
          title="No se encontraron usuarios"
          description="Intentá ajustar los filtros de búsqueda."
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Roles
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Registrado
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {usuarios.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-gray-900">
                      {[u.nombre, u.apellido].filter(Boolean).join(' ') || '—'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{u.email}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {u.roles.length > 0
                        ? u.roles.map((r) => <RoleBadge key={r} rol={r} />)
                        : <span className="text-xs text-gray-400">Sin rol</span>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        u.activo
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {u.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {u.created_at
                      ? new Date(u.created_at).toLocaleDateString('es-AR')
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingUser(u)}
                      >
                        Editar
                      </Button>
                      <Button
                        variant={u.activo ? 'ghost' : 'secondary'}
                        size="sm"
                        disabled={toggleEstado.isPending}
                        onClick={() => handleToggleEstado(u)}
                      >
                        {u.activo ? 'Desactivar' : 'Activar'}
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {pages > 1 && (
        <div className="mt-4">
          <OrderPagination
            page={page}
            pages={pages}
            total={total}
            onPageChange={setPage}
          />
        </div>
      )}

      {/* Edit modal */}
      {editingUser && (
        <EditModal
          usuario={editingUser}
          onClose={() => setEditingUser(null)}
          onSave={handleSaveEdit}
          isLoading={actualizarUsuario.isPending}
        />
      )}
    </div>
  )
}
