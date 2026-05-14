import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { listarPedidos } from '@/entities/pedidos'
import type { ListarPedidosParams } from '@/entities/pedidos'

interface UseListarPedidosOptions {
  params?: ListarPedidosParams
}

export function useListarPedidos({ params = {} }: UseListarPedidosOptions = {}) {
  const { page = 1, size = 20, estado, fecha_desde, fecha_hasta } = params

  return useQuery({
    queryKey: ['pedidos', { page, size, estado, fecha_desde, fecha_hasta }],
    queryFn: () =>
      listarPedidos({
        page,
        size,
        estado: estado || undefined,
        fecha_desde: fecha_desde || undefined,
        fecha_hasta: fecha_hasta || undefined,
      }),
    placeholderData: keepPreviousData,
  })
}
