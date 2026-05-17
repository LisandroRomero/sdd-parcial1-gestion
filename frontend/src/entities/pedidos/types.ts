export interface DetallePedidoCreate {
  producto_id: number
  cantidad: number
  personalizacion?: number[]
}

export interface PedidoCreate {
  direccion_id: number
  forma_pago_codigo: string
  detalles: DetallePedidoCreate[]
}

export interface DireccionSnapshot {
  id: number
  calle: string
  numero: string
  piso?: string
  departamento?: string
  ciudad: string
  provincia: string
  codigo_postal?: string
}

/** Compact order schema for listings — no details, history, or payment data. */
export interface PedidoRead {
  id: number
  usuario_id: number
  estado_actual: string
  total: string
  costo_envio: string
  created_at: string
  cantidad_items: number
}

export interface PagoResumen {
  id: number
  estado_pago: string | null
  metodo_pago: string | null
  monto: string
}

/** Full order detail — extends PedidoRead with items, history, and payment. */
export interface PedidoDetail extends PedidoRead {
  detalles: DetallePedidoRead[]
  historial_estados: HistorialEstadoRead[]
  pago: PagoResumen | null
  direccion?: DireccionSnapshot | null
}

export interface DetallePedidoRead {
  id: number
  producto_id: number
  nombre_snapshot: string
  precio_snapshot: string
  cantidad: number
  subtotal: string
}

export interface AvanzarEstadoRequest {
  nuevo_estado: string
  motivo?: string
}

export interface HistorialEstadoRead {
  id: number
  pedido_id: number
  estado_desde: string | null
  estado_hasta: string
  usuario_id: number | null
  motivo: string | null
  created_at: string
}

/** Paginated order list response with page/size format. */
export interface PedidoListRead {
  items: PedidoRead[]
  total: number
  page: number
  size: number
  pages: number
}

/** Sort field for order listing. */
export type SortField = 'id' | 'total' | 'created_at'

/** Sort direction for order listing. */
export type SortOrder = 'asc' | 'desc'

/** Parameters for listing orders with pagination and filters. */
export interface ListarPedidosParams {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  size?: number
  buscar?: string
  sort_by?: SortField
  sort_order?: SortOrder
}

/** Parameters for admin order listing — includes user_id filter + sort. */
export interface ListarPedidosAdminParams extends ListarPedidosParams {
  usuario_id?: number
  sort_by?: SortField
  sort_order?: SortOrder
}
