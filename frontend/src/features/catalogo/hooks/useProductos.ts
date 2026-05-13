import { useQuery } from '@tanstack/react-query'
import { fetchProductos } from '@/entities/producto'
import type { ProductoFiltros } from '@/entities/producto'

export function useProductos(filtros: ProductoFiltros) {
  return useQuery({
    queryKey: ['productos', filtros],
    queryFn: () => fetchProductos(filtros),
  })
}
