import { useMutation, useQueryClient } from '@tanstack/react-query'
import { eliminarIngrediente } from '../api/adminIngredientesApi'

export function useEliminarIngrediente() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => eliminarIngrediente(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredientes-admin'] })
    },
  })
}
