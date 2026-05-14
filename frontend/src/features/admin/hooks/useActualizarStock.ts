import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { StockUpdate } from '@/entities/producto/types'
import { actualizarStockAdmin } from '../api/adminProductosApi'

export function useActualizarStock() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: StockUpdate }) =>
      actualizarStockAdmin(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-productos'] })
    },
  })
}
