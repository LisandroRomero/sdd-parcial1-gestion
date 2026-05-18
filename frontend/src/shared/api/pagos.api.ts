import { api } from './axios'

export interface CrearPagoRequest {
  pedido_id: number
  card_token: string
  payment_method_id: string
  monto: string
}

export interface PagoResponse {
  id: number
  pedido_id: number
  mp_payment_id: number | null
  mp_status: string | null
  external_reference: string | null
  monto: string
  moneda: string
  created_at: string | null
}

export async function crearPago(data: CrearPagoRequest): Promise<PagoResponse> {
  const { data: response } = await api.post<PagoResponse>('/pagos/crear', data)
  return response
}
