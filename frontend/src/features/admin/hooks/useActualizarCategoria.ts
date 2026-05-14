import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { CategoriaUpdate } from '@/entities/admin/types'
import { actualizarCategoria } from '../api/adminCategoriasApi'

export function useActualizarCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: CategoriaUpdate }) =>
      actualizarCategoria(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias-admin'] })
    },
  })
}
