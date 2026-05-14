import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { EstadoUsuarioUpdate } from '@/entities/admin/types'
import { toggleEstadoUsuario } from '../api/adminUsuariosApi'

export function useToggleEstadoUsuario() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: EstadoUsuarioUpdate }) =>
      toggleEstadoUsuario(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'usuarios'] })
    },
  })
}
