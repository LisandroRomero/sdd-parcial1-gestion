import { useQuery } from '@tanstack/react-query'
import { fetchCategorias } from '@/entities/producto'

export function useCategorias() {
  return useQuery({
    queryKey: ['categorias'],
    queryFn: fetchCategorias,
    staleTime: Infinity,
  })
}
