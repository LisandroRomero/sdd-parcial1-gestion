import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { IngredienteUpdate } from '@/entities/admin/types'
import { actualizarIngrediente } from '../api/adminIngredientesApi'

export function useActualizarIngrediente() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: IngredienteUpdate }) =>
      actualizarIngrediente(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredientes-admin'] })
    },
  })
}
