import { api } from '@/shared/api'
import type { PerfilRead, PerfilUpdate } from './types'

export const fetchPerfil = (): Promise<PerfilRead> =>
  api.get<PerfilRead>('/usuarios/me/perfil').then((r) => r.data)

export const updatePerfil = (data: PerfilUpdate): Promise<PerfilRead> =>
  api.put<PerfilRead>('/usuarios/me/perfil', data).then((r) => r.data)
