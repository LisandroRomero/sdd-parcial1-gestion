export interface PerfilRead {
  id: number
  nombre: string | null
  apellido: string | null
  email: string
  telefono: string | null
  roles: string[]
  activo: boolean
  created_at: string | null
  updated_at: string | null
  direcciones: import('@/entities/direcciones').DireccionEntregaRead[]
}

export interface PerfilUpdate {
  nombre?: string | null
  apellido?: string | null
  telefono?: string | null
}
