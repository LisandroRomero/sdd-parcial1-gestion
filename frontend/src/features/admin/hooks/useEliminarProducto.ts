import { useMutation, useQueryClient } from '@tanstack/react-query'
import { eliminarProducto } from '../api/adminProductosApi'

export function useEliminarProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => eliminarProducto(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
    },
  })
}
