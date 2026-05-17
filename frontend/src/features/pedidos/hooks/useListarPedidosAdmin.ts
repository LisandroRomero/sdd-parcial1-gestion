import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { listarPedidos } from '@/entities/pedidos'
import type { ListarPedidosAdminParams } from '@/entities/pedidos'

interface UseListarPedidosAdminOptions {
  params?: ListarPedidosAdminParams
}

export function useListarPedidosAdmin({ params = {} }: UseListarPedidosAdminOptions = {}) {
  const { page = 1, size = 20, estado, fecha_desde, fecha_hasta, buscar, sort_by, sort_order } = params

  return useQuery({
    queryKey: ['pedidos-admin', { page, size, estado, fecha_desde, fecha_hasta, buscar, sort_by, sort_order }],
    queryFn: () =>
      listarPedidos({
        page,
        size,
        estado: estado || undefined,
        fecha_desde: fecha_desde || undefined,
        fecha_hasta: fecha_hasta || undefined,
        buscar: buscar || undefined,
        sort_by: sort_by || undefined,
        sort_order: sort_order || undefined,
      }),
    placeholderData: keepPreviousData,
    refetchInterval: 30000,
  })
}
