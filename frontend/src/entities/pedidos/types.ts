export interface DetallePedidoCreate {
  producto_id: number
  cantidad: number
  precio_unitario: string
  ingredientes_excluidos?: number[]
}

export interface PedidoCreate {
  direccion_entrega_id: number
  detalles: DetallePedidoCreate[]
}

export interface PedidoRead {
  id: number
  usuario_id: number
  estado: string
  total: string
  created_at: string
  updated_at?: string
  direccion_entrega_id: number
  detalles: DetallePedidoRead[]
}

export interface DetallePedidoRead {
  id: number
  producto_id: number
  nombre_producto: string
  cantidad: number
  precio_unitario: string
  subtotal: string
  ingredientes_excluidos?: number[]
}
