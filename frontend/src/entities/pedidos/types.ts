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

/** Compact order schema for listings — no details, history, or payment data. */
export interface PedidoRead {
  id: number
  usuario_id: number
  estado_actual: string
  total: string
  costo_envio: string
  created_at: string
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

/** Parameters for listing orders with pagination and filters. */
export interface ListarPedidosParams {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  size?: number
}
