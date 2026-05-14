import { api } from '@/shared/api'
import type { DireccionEntregaRead, DireccionEntregaCreate, DireccionEntregaUpdate } from './types'

export const fetchDirecciones = (): Promise<DireccionEntregaRead[]> =>
  api.get<DireccionEntregaRead[]>('/usuarios/me/direcciones').then((r) => r.data)

export const createDireccion = (data: DireccionEntregaCreate): Promise<DireccionEntregaRead> =>
  api.post<DireccionEntregaRead>('/usuarios/me/direcciones', data).then((r) => r.data)

export const updateDireccion = (id: number, data: DireccionEntregaUpdate): Promise<DireccionEntregaRead> =>
  api.put<DireccionEntregaRead>(`/usuarios/me/direcciones/${id}`, data).then((r) => r.data)

export const deleteDireccion = (id: number): Promise<void> =>
  api.delete(`/usuarios/me/direcciones/${id}`).then(() => undefined)

export const setDireccionPrincipal = (id: number): Promise<DireccionEntregaRead> =>
  api.patch<DireccionEntregaRead>(`/usuarios/me/direcciones/${id}/principal`).then((r) => r.data)
