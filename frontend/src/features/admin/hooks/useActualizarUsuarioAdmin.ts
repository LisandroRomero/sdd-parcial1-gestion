import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { AdminUsuarioUpdate } from '@/entities/admin/types'
import { actualizarUsuarioAdmin } from '../api/adminUsuariosApi'

export function useActualizarUsuarioAdmin() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: AdminUsuarioUpdate }) =>
      actualizarUsuarioAdmin(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'usuarios'] })
    },
  })
}
