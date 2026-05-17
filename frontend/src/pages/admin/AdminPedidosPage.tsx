import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import { listarPedidos, avanzarEstado } from '@/entities/pedidos'
import { statusColors, statusLabels, getNextState } from '@/entities/pedidos/constants'
import type { ListarPedidosParams } from '@/entities/pedidos'
import { CancelarPedidoModal } from '@/features/pedidos'
import { LoadingSpinner, ErrorMessage, EmptyState, OfflineMessage, NoPermissionMessage } from '@/shared/ui'
import { Button } from '@/shared/components'
import { getAuthErrorStatus, getErrorMessage } from '@/shared/api'
import { useOffline } from '@/shared/lib/hooks'
import { OrderPagination } from '@/features/pedidos/components/OrderPagination'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const ARS = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })

function formatARS(value: string) {
  return ARS.format(parseFloat(value))
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-AR')
}

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------
function StatusBadge({ estado }: { estado: string }) {
  const color = statusColors[estado] ?? 'bg-gray-100 text-gray-700 border-gray-300'
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${color}`}
    >
      {statusLabels[estado] ?? estado}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export function AdminPedidosPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isOffline = useOffline()

  // Filters state
  const [buscarInput, setBuscarInput] = useState('')
  const [buscar, setBuscar] = useState<string | undefined>(undefined)
  const [estado, setEstado] = useState<string | undefined>(undefined)
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [page, setPage] = useState(1)

  // UI state
  const [openDropdownId, setOpenDropdownId] = useState<number | null>(null)
  const [advancingRowId, setAdvancingRowId] = useState<number | null>(null)
  const [cancelPedidoId, setCancelPedidoId] = useState<number | null>(null)
  const dropdownRef = useRef<HTMLDivElement | null>(null)

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpenDropdownId(null)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // Query params
  const params: ListarPedidosParams = {
    page,
    size: 20,
    ...(buscar && { buscar }),
    ...(estado && { estado }),
    ...(fechaDesde && { fecha_desde: fechaDesde }),
    ...(fechaHasta && { fecha_hasta: fechaHasta }),
  }

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['pedidos-admin', params],
    queryFn: () => listarPedidos(params),
    placeholderData: keepPreviousData,
    refetchInterval: 30000,
  })

  // Advance state mutation
  const advanceMutation = useMutation({
    mutationFn: ({ pedidoId, nuevoEstado }: { pedidoId: number; nuevoEstado: string }) =>
      avanzarEstado(pedidoId, { nuevo_estado: nuevoEstado }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pedidos-admin'] })
      setAdvancingRowId(null)
    },
  })

  const authStatus = isError ? getAuthErrorStatus(error) : undefined

  // --- Debounced search ---
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

  function handleEstadoChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setEstado(e.target.value || undefined)
    setPage(1)
  }

  function handleFechaDesdeChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFechaDesde(e.target.value)
    setPage(1)
  }

  function handleFechaHastaChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFechaHasta(e.target.value)
    setPage(1)
  }

  function handleFilter() {
    setBuscar(buscarInput || undefined)
    setPage(1)
  }

  function handleClearFilters() {
    setBuscarInput('')
    setBuscar(undefined)
    setEstado(undefined)
    setFechaDesde('')
    setFechaHasta('')
    setPage(1)
  }

  function handleCancelModalClose() {
    setCancelPedidoId(null)
    queryClient.invalidateQueries({ queryKey: ['pedidos-admin'] })
  }

  // Loading state (no data yet)
  if (isLoading && !data) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner />
      </div>
    )
  }

  // Error state (no data)
  if (isError && !data) {
    return authStatus ? (
      <NoPermissionMessage status={authStatus} />
    ) : (
      <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
    )
  }

  const pedidos = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 0

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Gestión de pedidos</h1>
      {isOffline && <div className="mb-4"><OfflineMessage /></div>}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          type="text"
          placeholder="Buscar por N° de pedido…"
          value={buscarInput}
          onChange={handleBuscarChange}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <select
          value={estado ?? ''}
          onChange={handleEstadoChange}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
        >
          <option value="">Todos los estados</option>
          {Object.entries(statusLabels).map(([codigo, label]) => (
            <option key={codigo} value={codigo}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6 items-end">
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Desde</label>
          <input
            type="date"
            value={fechaDesde}
            onChange={handleFechaDesdeChange}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div className="flex-1 min-w-[150px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
          <input
            type="date"
            value={fechaHasta}
            onChange={handleFechaHastaChange}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div className="flex items-center gap-2 pb-0.5">
          <Button variant="primary" size="sm" onClick={handleFilter}>
            Filtrar
          </Button>
          {(buscar || estado || fechaDesde || fechaHasta) && (
            <Button variant="ghost" size="sm" onClick={handleClearFilters}>
              Limpiar
            </Button>
          )}
        </div>
      </div>

      {/* Table */}
      {pedidos.length === 0 ? (
        <EmptyState
          title="No se encontraron pedidos"
          description="Intentá ajustar los filtros de búsqueda."
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  N° Pedido
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Ítems
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Total
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
              {pedidos.map((pedido) => {
                const nextState = getNextState(pedido.estado_actual, ['ADMIN'])

                return (
                  <tr key={pedido.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      #{pedido.id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      Usuario #{pedido.usuario_id}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge estado={pedido.estado_actual} />
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{pedido.cantidad_items}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium whitespace-nowrap">
                      {formatARS(pedido.total)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                      {formatDate(pedido.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="relative inline-block text-left">
                        <button
                          type="button"
                          onClick={() =>
                            setOpenDropdownId(openDropdownId === pedido.id ? null : pedido.id)
                          }
                          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                          aria-label="Opciones"
                        >
                          <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zm0 6a2 2 0 110-4 2 2 0 010 4zm0 6a2 2 0 110-4 2 2 0 010 4z" />
                          </svg>
                        </button>

                        {openDropdownId === pedido.id && (
                          <div
                            ref={dropdownRef}
                            className="absolute right-0 z-10 mt-1 w-48 rounded-lg border border-gray-200 bg-white shadow-lg py-1"
                          >
                            <button
                              onClick={() => {
                                setOpenDropdownId(null)
                                navigate(`/admin/pedidos/${pedido.id}`)
                              }}
                              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                            >
                              Ver detalle
                            </button>

                            {nextState && (
                              <button
                                onClick={() => {
                                  setOpenDropdownId(null)
                                  setAdvancingRowId(
                                    advancingRowId === pedido.id ? null : pedido.id,
                                  )
                                }}
                                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                              >
                                Avanzar estado
                              </button>
                            )}

                            <button
                              onClick={() => {
                                setOpenDropdownId(null)
                                setCancelPedidoId(pedido.id)
                              }}
                              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                            >
                              Cancelar pedido
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}

              {/* Inline advance state row */}
              {advancingRowId !== null &&
                (() => {
                  const pedido = pedidos.find((p) => p.id === advancingRowId)
                  if (!pedido) return null
                  const nextState = getNextState(pedido.estado_actual, ['ADMIN'])
                  if (!nextState) return null

                  return (
                    <tr key={`advance-${pedido.id}`}>
                      <td colSpan={7} className="px-4 py-3 bg-blue-50">
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-gray-700">
                            Avanzar pedido{' '}
                            <span className="font-semibold">#{pedido.id}</span> de{' '}
                            <span className="font-medium">
                              {statusLabels[pedido.estado_actual]}
                            </span>{' '}
                            →{' '}
                            <span className="font-medium">{statusLabels[nextState]}</span>
                          </span>
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={advanceMutation.isPending}
                            onClick={() =>
                              advanceMutation.mutate({
                                pedidoId: pedido.id,
                                nuevoEstado: nextState,
                              })
                            }
                          >
                            {advanceMutation.isPending ? 'Avanzando…' : 'Confirmar'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={advanceMutation.isPending}
                            onClick={() => setAdvancingRowId(null)}
                          >
                            Cancelar
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })()}
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

      {/* Cancel modal */}
      {cancelPedidoId !== null && (
        <CancelarPedidoModal
          pedidoId={cancelPedidoId}
          isOpen={true}
          onClose={handleCancelModalClose}
        />
      )}
    </div>
  )
}
