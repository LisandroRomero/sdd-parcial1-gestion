import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cancelarPedido } from '@/entities/pedidos'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { getErrorMessage } from '@/shared/api'

const ERROR_MESSAGES: Record<string, string> = {
  PEDIDO_ESTADO_TERMINAL: 'El pedido ya está en un estado terminal. No se puede cancelar.',
  PEDIDO_NO_ENCONTRADO: 'El pedido no existe o fue eliminado.',
  PEDIDO_ROL_NO_AUTORIZADO: 'No tenés permiso para cancelar este pedido.',
  PEDIDO_MOTIVO_REQUERIDO: 'El motivo de cancelación es obligatorio.',
  PEDIDO_STOCK_INSUFICIENTE: 'No se pudo restaurar el stock. Contactá a soporte.',
}

const DEFAULT_ERROR = 'Error al cancelar el pedido. Intentá de nuevo.'

const ROLES_CAN_CANCEL: Record<string, string[]> = {
  CLIENT: ['PENDIENTE', 'CONFIRMADO'],
  ADMIN: ['PENDIENTE', 'CONFIRMADO', 'EN_PREP'],
  PEDIDOS: ['PENDIENTE', 'CONFIRMADO'],
}

export function canCancel(estado: string, roles: string[]): boolean {
  return roles.some((rol) => ROLES_CAN_CANCEL[rol]?.includes(estado))
}

export function useCancelarPedido() {
  const queryClient = useQueryClient()
  const showToast = useUIStore((s) => s.showToast)

  return useMutation({
    mutationFn: ({ pedidoId, motivo }: { pedidoId: number; motivo: string }) =>
      cancelarPedido(pedidoId, motivo),
    onSuccess: (_data, { pedidoId }) => {
      queryClient.invalidateQueries({ queryKey: ['pedidos'] })
      queryClient.invalidateQueries({ queryKey: ['pedido', pedidoId] })
      queryClient.invalidateQueries({ queryKey: ['pedidos-admin'] })
    },
    onError: (error) => {
      const errorCode = (error as { response?: { data?: { error_code?: string } } })?.response?.data?.error_code
      const message = errorCode ? (ERROR_MESSAGES[errorCode] ?? DEFAULT_ERROR) : getErrorMessage(error)
      showToast(message, 'error')
    },
  })
}
