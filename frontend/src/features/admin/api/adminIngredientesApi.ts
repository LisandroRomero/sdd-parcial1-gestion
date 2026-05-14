import { api } from '@/shared/api'
import type {
  IngredienteAdminRead,
  IngredienteCreate,
  IngredienteUpdate,
  IngredientePaginado,
} from '@/entities/admin/types'

export const listarIngredientesAdmin = (
  page = 1,
  size = 100,
): Promise<IngredientePaginado> =>
  api
    .get<IngredientePaginado>('/ingredientes', { params: { page, size } })
    .then((r) => r.data)

export const crearIngrediente = (
  body: IngredienteCreate,
): Promise<IngredienteAdminRead> =>
  api
    .post<IngredienteAdminRead>('/ingredientes/', body)
    .then((r) => r.data)

export const actualizarIngrediente = (
  id: number,
  body: IngredienteUpdate,
): Promise<IngredienteAdminRead> =>
  api
    .put<IngredienteAdminRead>(`/ingredientes/${id}`, body)
    .then((r) => r.data)

export const eliminarIngrediente = (id: number): Promise<void> =>
  api.delete(`/ingredientes/${id}`).then(() => undefined)
