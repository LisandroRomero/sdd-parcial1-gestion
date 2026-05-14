import { useQuery } from '@tanstack/react-query'
import { listarIngredientesAdmin } from '../api/adminIngredientesApi'

export function useListarIngredientesAdmin(page = 1, size = 100) {
  return useQuery({
    queryKey: ['ingredientes-admin', page, size],
    queryFn: () => listarIngredientesAdmin(page, size),
  })
}
