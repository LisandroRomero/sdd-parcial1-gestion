import { keepPreviousData, useQuery } from '@tanstack/react-query'
import type { AdminUsuariosParams } from '@/entities/admin/types'
import { listarUsuariosAdmin } from '../api/adminUsuariosApi'

export function useListarUsuariosAdmin(params?: AdminUsuariosParams) {
  return useQuery({
    queryKey: ['admin', 'usuarios', params],
    queryFn: () => listarUsuariosAdmin(params),
    placeholderData: keepPreviousData,
  })
}
