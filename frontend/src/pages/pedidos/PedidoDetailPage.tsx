import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getPedido } from '@/entities/pedidos'
import { statusColors, statusLabels, getNextState } from '@/entities/pedidos/constants'
import { OrderTimeline } from '@/entities/pedidos/ui/OrderTimeline'
import { canCancel, useCancelarPedido, CancelarPedidoModal } from '@/features/pedidos'
import { useAvanzarEstado } from '@/features/pedidos/hooks/useAvanzarEstado'
import { useAuthStore } from '@/shared/lib/stores/auth.store'
import { LoadingSpinner, ErrorMessage, EmptyState } from '@/shared/ui'
import { Button, Card, CardHeader, CardContent } from '@/shared/components'

const formatARS = (value: string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(parseFloat(value))

const PAYMENT_LABELS: Record<string, string> = {
  TARJETA: 'Tarjeta',
  RAPIPAGO: 'Rapipago',
  PAGO_FACIL: 'Pago Fácil',
}

const PAYMENT_STATUS_LABELS: Record<string, string> = {
  approved: 'Aprobado',
  rejected: 'Rechazado',
  in_process: 'En proceso',
  pending: 'Pendiente',
}

const formatDate = (dateString: string) =>
  new Intl.DateTimeFormat('es-AR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(dateString))

function usePedido(id: number) {
  return useQuery({
    queryKey: ['pedido', id],
    queryFn: () => getPedido(id),
    enabled: !!id,
  })
}

export function PedidoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const numericId = id ? parseInt(id, 10) : 0
  const user = useAuthStore((s) => s.user)

  const { data: pedido, isLoading, isError, error, refetch } = usePedido(numericId)
  const cancelMutation = useCancelarPedido()
  const avanzarMutation = useAvanzarEstado(numericId)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCancelling, setIsCancelling] = useState(false)

  useEffect(() => {
    if (cancelMutation.isPending) return
    if (cancelMutation.isError) {
      const err = cancelMutation.error as { response?: { data?: { error_code?: string } } }
      if (err?.response?.data?.error_code === 'PEDIDO_ESTADO_TERMINAL') {
        refetch()
      }
    }
  }, [cancelMutation.isPending, cancelMutation.isError, cancelMutation.error, refetch])

  const roles = user?.roles ?? []
  const is404 = isError && (error as { response?: { status?: number } })?.response?.status === 404

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isError && is404) {
    return (
      <EmptyState
        title="Pedido no encontrado"
        description="El pedido que buscás no existe o fue eliminado."
      />
    )
  }

  if (isError) {
    return (
      <ErrorMessage
        message={error instanceof Error ? error.message : 'Error al cargar el pedido'}
        onRetry={refetch}
      />
    )
  }

  if (!pedido) {
    return (
      <EmptyState
        title="Pedido no encontrado"
        description="No encontramos información de este pedido."
      />
    )
  }

  const showCancelButton = canCancel(pedido.estado_actual, roles)
  const nextState = getNextState(pedido.estado_actual, roles)

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Pedido #{pedido.id}
        </h1>
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${
            statusColors[pedido.estado_actual] ?? 'bg-gray-100 text-gray-800 border-gray-300'
          }`}
        >
          {pedido.estado_actual === 'CANCELADO' && (
            <span className="text-base font-bold leading-none">×</span>
          )}
          {statusLabels[pedido.estado_actual] ?? pedido.estado_actual}
        </span>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900">Información del pedido</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Estado</p>
              <p className="font-medium text-gray-900">
                {statusLabels[pedido.estado_actual] ?? pedido.estado_actual}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total</p>
              <p className="font-medium text-gray-900">{formatARS(pedido.total)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Costo de envío</p>
              <p className="font-medium text-gray-900">{formatARS(pedido.costo_envio)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Fecha</p>
              <p className="font-medium text-gray-900">{formatDate(pedido.created_at)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {pedido.pago && (
        <Card className="mb-6">
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Información de pago</h2>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Método de pago</p>
                <p className="font-medium text-gray-900">
                  {PAYMENT_LABELS[pedido.pago.metodo_pago ?? ''] ?? pedido.pago.metodo_pago ?? '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Estado del pago</p>
                <p className="font-medium text-gray-900">
                  {PAYMENT_STATUS_LABELS[pedido.pago.estado_pago ?? ''] ?? pedido.pago.estado_pago ?? '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Monto</p>
                <p className="font-medium text-gray-900">{formatARS(pedido.pago.monto)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {pedido.direccion && (
        <Card className="mb-6">
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Dirección de entrega</h2>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="font-medium text-gray-900">
              {pedido.direccion.calle} {pedido.direccion.numero}
            </p>
            {(pedido.direccion.piso || pedido.direccion.departamento) && (
              <p className="text-sm text-gray-600">
                {[pedido.direccion.piso && `Piso ${pedido.direccion.piso}`, pedido.direccion.departamento && `Dpto. ${pedido.direccion.departamento}`].filter(Boolean).join(', ')}
              </p>
            )}
            <p className="text-sm text-gray-600">
              {pedido.direccion.ciudad}, {pedido.direccion.provincia}
            </p>
          </CardContent>
        </Card>
      )}

      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900">Productos</h2>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-gray-100">
            {pedido.detalles.map((detalle) => (
              <div key={detalle.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium text-gray-900">{detalle.nombre_snapshot}</p>
                  <p className="text-sm text-gray-500">
                    {detalle.cantidad} × {formatARS(detalle.precio_snapshot)}
                  </p>
                </div>
                <p className="font-medium text-gray-900">{formatARS(detalle.subtotal)}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900">Historial de estados</h2>
        </CardHeader>
        <CardContent>
          <OrderTimeline historial={pedido.historial_estados} />
        </CardContent>
      </Card>

      {(nextState || showCancelButton) && (
        <div className="flex flex-col gap-2 items-end">
          {nextState && (
            <div>
              <Button
                variant="primary"
                onClick={() => avanzarMutation.mutate({ nuevo_estado: nextState })}
                disabled={avanzarMutation.isPending}
              >
                {avanzarMutation.isPending ? 'Avanzando...' : `Avanzar a ${statusLabels[nextState] ?? nextState}`}
              </Button>
              {avanzarMutation.isError && (
                <p className="text-sm text-red-600 mt-1">
                  {(avanzarMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Error al avanzar el estado'}
                </p>
              )}
            </div>
          )}
          {showCancelButton && (
            <Button
              variant="primary"
              className="bg-red-600 text-white hover:bg-red-700"
              onClick={() => setIsModalOpen(true)}
              disabled={isCancelling}
            >
              {isCancelling ? 'Cancelando...' : 'Cancelar pedido'}
            </Button>
          )}
        </div>
      )}

      <CancelarPedidoModal
        pedidoId={numericId}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          refetch()
        }}
        onMutationChange={setIsCancelling}
      />
    </div>
  )
}
