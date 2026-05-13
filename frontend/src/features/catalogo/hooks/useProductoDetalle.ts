import { useQuery } from '@tanstack/react-query'
import { fetchProductoDetalle } from '@/entities/producto'

export function useProductoDetalle(id: number) {
  return useQuery({
    queryKey: ['producto', id],
    queryFn: () => fetchProductoDetalle(id),
    enabled: id > 0,
  })
}
