export interface ProductoFiltros {
  page?: number
  size?: number
  categoria_id?: number
  precio_min?: number
  precio_max?: number
  busqueda?: string
  tiene_alergenos?: boolean
}

export interface ProductoPaginado {
  items: ProductoRead[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ProductoIngredienteRead {
  ingrediente_id: number
  nombre: string
  es_alergeno: boolean
  cantidad: number | null
  unidad: string | null
  es_removible: boolean
}

export interface CategoriaRead {
  id: number
  nombre: string
  descripcion: string | null
}

export interface ProductoRead {
  id: number
  codigo_sku: string
  nombre: string
  descripcion: string | null
  precio_base: string // Decimal comes as string from API
  stock_cantidad: number
  disponible: boolean
  imagen_url: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ProductoDetalleRead extends ProductoRead {
  categorias: CategoriaRead[]
  ingredientes: ProductoIngredienteRead[]
  tiene_alergenos: boolean
}

export interface ProductoCreate {
  codigo_sku: string
  nombre: string
  descripcion?: string
  precio_base: string
  stock_cantidad: number
  disponible: boolean
  imagen_url?: string
  categoria_ids: number[]
}

export interface ProductoUpdate {
  codigo_sku?: string
  nombre?: string
  descripcion?: string
  precio_base?: string
  stock_cantidad?: number
  disponible?: boolean
  imagen_url?: string
  categoria_ids?: number[]
}

export interface StockUpdate {
  stock_cantidad: number
}

export interface DisponibilidadUpdate {
  disponible: boolean
}
