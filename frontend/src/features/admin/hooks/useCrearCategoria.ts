import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { CategoriaCreate } from '@/entities/admin/types'
import { crearCategoria } from '../api/adminCategoriasApi'

export function useCrearCategoria() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: CategoriaCreate) => crearCategoria(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias-admin'] })
    },
  })
}
