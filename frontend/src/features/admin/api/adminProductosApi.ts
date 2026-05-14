import { api } from '@/shared/api'
import type {
  ProductoCreate,
  ProductoUpdate,
  ProductoRead,
  ProductoPaginado,
  StockUpdate,
  DisponibilidadUpdate,
} from '@/entities/producto/types'

export const crearProducto = (body: ProductoCreate): Promise<ProductoRead> =>
  api.post<ProductoRead>('/productos/', body).then((r) => r.data)

export const actualizarProducto = (
  id: number,
  body: ProductoUpdate,
): Promise<ProductoRead> =>
  api.put<ProductoRead>(`/productos/${id}`, body).then((r) => r.data)

export const eliminarProducto = (id: number): Promise<void> =>
  api.delete(`/productos/${id}`).then(() => undefined)

export const actualizarStockAdmin = (
  id: number,
  body: StockUpdate,
): Promise<ProductoRead> =>
  api
    .patch<ProductoRead>(`/productos/${id}/stock`, body)
    .then((r) => r.data)

export const cambiarDisponibilidad = (
  id: number,
  body: DisponibilidadUpdate,
): Promise<ProductoRead> =>
  api
    .patch<ProductoRead>(`/productos/${id}/disponibilidad`, body)
    .then((r) => r.data)

export const listarProductosAdmin = (
  params: { include_deleted?: boolean; page?: number; size?: number } = {},
): Promise<ProductoPaginado> =>
  api
    .get<ProductoPaginado>('/productos/', {
      params: { page: params.page ?? 1, size: params.size ?? 100, include_deleted: params.include_deleted ?? false },
    })
    .then((r) => r.data)
