import { api } from './axios'

export interface FormaPagoRead {
  codigo: string
  descripcion: string | null
  activo: boolean
}

export async function getFormasPago(): Promise<FormaPagoRead[]> {
  const { data } = await api.get<FormaPagoRead[]>('/pagos/formas-pago/')
  return data
}
