export interface DireccionEntregaRead {
  id: number
  usuario_id: number
  alias: string
  calle: string
  numero: string
  piso: string | null
  departamento: string | null
  ciudad: string
  provincia: string
  codigo_postal: string
  es_principal: boolean
  deleted_at: string | null
  created_at: string
  updated_at: string
}

export interface DireccionEntregaCreate {
  alias: string
  calle: string
  numero: string
  piso?: string | null
  departamento?: string | null
  ciudad: string
  provincia: string
  codigo_postal: string
  es_principal?: boolean
}

export interface DireccionEntregaUpdate {
  alias?: string | null
  calle?: string | null
  numero?: string | null
  piso?: string | null
  departamento?: string | null
  ciudad?: string | null
  provincia?: string | null
  codigo_postal?: string | null
  es_principal?: boolean | null
}
