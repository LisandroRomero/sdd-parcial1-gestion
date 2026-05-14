import { api } from '@/shared/api'
import type {
  AdminUsuarioListRead,
  AdminUsuarioRead,
  AdminUsuarioUpdate,
  AdminUsuariosParams,
  EstadoUsuarioUpdate,
} from '@/entities/admin/types'

export const listarUsuariosAdmin = (
  params?: AdminUsuariosParams,
): Promise<AdminUsuarioListRead> =>
  api
    .get<AdminUsuarioListRead>('/admin/usuarios', { params })
    .then((r) => r.data)

export const actualizarUsuarioAdmin = (
  id: number,
  body: AdminUsuarioUpdate,
): Promise<AdminUsuarioRead> =>
  api
    .put<AdminUsuarioRead>(`/admin/usuarios/${id}`, body)
    .then((r) => r.data)

export const toggleEstadoUsuario = (
  id: number,
  body: EstadoUsuarioUpdate,
): Promise<AdminUsuarioRead> =>
  api
    .patch<AdminUsuarioRead>(`/admin/usuarios/${id}/estado`, body)
    .then((r) => r.data)
