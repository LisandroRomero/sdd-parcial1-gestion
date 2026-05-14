import { api } from '@/shared/api/axios'
import type { PedidoCreate, PedidoRead } from './types'

export const createPedido = (data: PedidoCreate): Promise<PedidoRead> =>
  api.post<PedidoRead>('/api/v1/pedidos', data).then((r) => r.data)
