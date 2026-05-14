import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { IngredienteCreate } from '@/entities/admin/types'
import { crearIngrediente } from '../api/adminIngredientesApi'

export function useCrearIngrediente() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: IngredienteCreate) => crearIngrediente(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredientes-admin'] })
    },
  })
}
