import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ProductoCreate } from '@/entities/producto/types'
import { crearProducto } from '../api/adminProductosApi'

export function useCrearProducto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: ProductoCreate) => crearProducto(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-productos'] })
    },
  })
}
