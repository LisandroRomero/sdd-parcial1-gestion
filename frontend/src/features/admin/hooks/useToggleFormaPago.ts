import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toggleFormaPago } from '../api/adminConfiguracionApi'
import type { FormaPagoUpdate } from '@/entities/admin/types'

export function useToggleFormaPago() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ codigo, body }: { codigo: string; body: FormaPagoUpdate }) =>
      toggleFormaPago(codigo, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['formas-pago'] })
    },
  })
}
