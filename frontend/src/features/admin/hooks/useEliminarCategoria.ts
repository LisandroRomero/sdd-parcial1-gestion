import { useMutation, useQueryClient } from '@tanstack/react-query'
import { eliminarCategoria } from '../api/adminCategoriasApi'

export function useEliminarCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => eliminarCategoria(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias-admin'] })
    },
  })
}
