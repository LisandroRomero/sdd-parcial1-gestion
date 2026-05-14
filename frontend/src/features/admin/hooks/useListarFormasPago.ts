import { useQuery } from '@tanstack/react-query'
import { listarFormasPago } from '../api/adminConfiguracionApi'
import type { FormaPagoRead } from '@/entities/admin/types'

export function useListarFormasPago() {
  return useQuery<FormaPagoRead[]>({
    queryKey: ['formas-pago'],
    queryFn: listarFormasPago,
  })
}
