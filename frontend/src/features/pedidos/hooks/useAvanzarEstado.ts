import { useMutation, useQueryClient } from '@tanstack/react-query'
import { avanzarEstado } from '@/entities/pedidos'
import type { AvanzarEstadoRequest } from '@/entities/pedidos'

export function useAvanzarEstado(pedidoId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: AvanzarEstadoRequest) => avanzarEstado(pedidoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pedido', pedidoId] })
    },
  })
}
