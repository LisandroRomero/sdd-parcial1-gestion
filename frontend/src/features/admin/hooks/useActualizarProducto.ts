import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ProductoUpdate } from '@/entities/producto/types'
import { actualizarProducto } from '../api/adminProductosApi'

export function useActualizarProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: ProductoUpdate }) =>
      actualizarProducto(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
    },
  })
}
