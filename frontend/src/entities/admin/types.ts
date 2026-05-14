export interface AdminUsuarioRead {
  id: number
  nombre: string | null
  apellido: string | null
  email: string
  activo: boolean
  roles: string[]
  created_at: string | null
}

export interface AdminUsuarioUpdate {
  nombre?: string
  apellido?: string
  email?: string
  roles?: string[]
}

export interface EstadoUsuarioUpdate {
  activo: boolean
}

export interface AdminUsuarioListRead {
  items: AdminUsuarioRead[]
  total: number
  page: number
  size: number
  pages: number
}

export interface AdminUsuariosParams {
  buscar?: string
  rol?: string
  page?: number
  size?: number
}

export interface CategoriaAdminRead {
  id: number
  nombre: string
  descripcion?: string | null
  parent_id?: number | null
  created_at?: string | null
}

export interface CategoriaCreate {
  nombre: string
  descripcion?: string
  parent_id?: number
}

export interface CategoriaUpdate {
  nombre?: string
  descripcion?: string
  parent_id?: number | null
}

export interface CategoriaPaginado {
  items: CategoriaAdminRead[]
  total: number
}

export interface IngredienteAdminRead {
  id: number
  nombre: string
  es_alergeno: boolean
  created_at?: string | null
}

export interface IngredienteCreate {
  nombre: string
  es_alergeno: boolean
}

export interface IngredienteUpdate {
  nombre?: string
  es_alergeno?: boolean
}

export interface IngredientePaginado {
  items: IngredienteAdminRead[]
  total: number
}
