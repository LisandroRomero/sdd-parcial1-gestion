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

export interface PedidoRead {
  id: number
  usuario_id: number
  estado_actual: string
  total: string
  costo_envio: string
  created_at: string
  updated_at?: string
  direccion_id: number
  detalles: DetallePedidoRead[]
  historial_estados: HistorialEstadoRead[]
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
