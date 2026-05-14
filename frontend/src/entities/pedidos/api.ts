import { api } from '@/shared/api/axios'
import type {
  AvanzarEstadoRequest,
  HistorialEstadoRead,
  ListarPedidosParams,
  PedidoCreate,
  PedidoDetail,
  PedidoListRead,
  PedidoRead,
} from './types'

export const createPedido = (data: PedidoCreate): Promise<PedidoRead> =>
  api.post<PedidoRead>('/api/v1/pedidos', data).then((r) => r.data)

export const avanzarEstado = (pedidoId: number, data: AvanzarEstadoRequest): Promise<PedidoRead> =>
  api.patch<PedidoRead>(`/api/v1/pedidos/${pedidoId}/estado`, data).then((r) => r.data)

export const cancelarPedido = (pedidoId: number, motivo: string): Promise<PedidoRead> =>
  api.delete<PedidoRead>(`/api/v1/pedidos/${pedidoId}`, { params: { motivo } }).then((r) => r.data)

export const getPedido = (pedidoId: number): Promise<PedidoDetail> =>
  api.get<PedidoDetail>(`/api/v1/pedidos/${pedidoId}`).then((r) => r.data)

export const listarPedidos = (params?: ListarPedidosParams): Promise<PedidoListRead> =>
  api.get<PedidoListRead>('/api/v1/pedidos', { params }).then((r) => r.data)

export const getHistorialPedido = (pedidoId: number): Promise<HistorialEstadoRead[]> =>
  api.get<HistorialEstadoRead[]>(`/api/v1/pedidos/${pedidoId}/historial`).then((r) => r.data)
