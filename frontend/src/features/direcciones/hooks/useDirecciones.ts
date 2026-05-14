import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchDirecciones,
  createDireccion,
  updateDireccion,
  deleteDireccion,
  setDireccionPrincipal,
} from '@/entities/direcciones'
import type { DireccionEntregaCreate, DireccionEntregaUpdate, DireccionEntregaRead } from '@/entities/direcciones'

export function useDirecciones() {
  return useQuery({
    queryKey: ['direcciones'],
    queryFn: fetchDirecciones,
  })
}

export function useCrearDireccion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: DireccionEntregaCreate) => createDireccion(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] })
    },
  })
}

export function useActualizarDireccion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: DireccionEntregaUpdate }) => updateDireccion(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] })
    },
  })
}

export function useEliminarDireccion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteDireccion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] })
    },
  })
}

export function useMarcarPrincipal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => setDireccionPrincipal(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['direcciones'] })
      const previous = queryClient.getQueryData<DireccionEntregaRead[]>(['direcciones'])
      if (previous) {
        queryClient.setQueryData<DireccionEntregaRead[]>(['direcciones'], (old) =>
          old?.map((d) => ({ ...d, es_principal: d.id === id })) ?? [],
        )
      }
      return { previous }
    },
    onError: (_err, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['direcciones'], context.previous)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['direcciones'] })
    },
  })
}
