import { useQuery } from '@tanstack/react-query'
import { listarCategoriasAdmin } from '../api/adminCategoriasApi'

export function useListarCategoriasAdmin() {
  return useQuery({
    queryKey: ['categorias-admin'],
    queryFn: listarCategoriasAdmin,
  })
}
