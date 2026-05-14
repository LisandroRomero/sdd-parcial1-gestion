import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { DisponibilidadUpdate } from '@/entities/producto/types'
import { cambiarDisponibilidad } from '../api/adminProductosApi'

export function useCambiarDisponibilidadAdmin() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: DisponibilidadUpdate }) =>
      cambiarDisponibilidad(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
    },
  })
}
