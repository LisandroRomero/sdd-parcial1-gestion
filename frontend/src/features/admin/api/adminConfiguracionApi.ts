import { api } from '@/shared/api'
import type { FormaPagoRead, FormaPagoUpdate } from '@/entities/admin/types'

export const listarFormasPago = (): Promise<FormaPagoRead[]> =>
  api.get<FormaPagoRead[]>('/admin/configuracion/formas-de-pago').then((r) => r.data)

export const toggleFormaPago = (
  codigo: string,
  body: FormaPagoUpdate,
): Promise<FormaPagoRead> =>
  api.patch<FormaPagoRead>(`/admin/configuracion/formas-de-pago/${codigo}`, body).then((r) => r.data)
