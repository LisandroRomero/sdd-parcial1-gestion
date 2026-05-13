import { api } from '@/shared/api'
import type { ProductoFiltros, ProductoPaginado, ProductoDetalleRead, CategoriaRead } from './types'

export const fetchProductos = (filtros: ProductoFiltros): Promise<ProductoPaginado> =>
  api.get<ProductoPaginado>('/productos', { params: filtros }).then((r) => r.data)

export const fetchProductoDetalle = (id: number): Promise<ProductoDetalleRead> =>
  api.get<ProductoDetalleRead>(`/productos/${id}`).then((r) => r.data)

export const fetchCategorias = (): Promise<{ items: CategoriaRead[]; total: number }> =>
  api.get<{ items: CategoriaRead[]; total: number }>('/categorias').then((r) => r.data)
