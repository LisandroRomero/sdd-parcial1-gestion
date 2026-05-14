import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchPerfil, updatePerfil } from '@/entities/perfil'
import type { PerfilUpdate } from '@/entities/perfil'

export function usePerfil() {
  return useQuery({
    queryKey: ['perfil'],
    queryFn: fetchPerfil,
  })
}

export function useActualizarPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: PerfilUpdate) => updatePerfil(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['perfil'] })
    },
  })
}
