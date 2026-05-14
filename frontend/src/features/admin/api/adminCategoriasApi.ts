import { api } from '@/shared/api'
import type {
  CategoriaAdminRead,
  CategoriaCreate,
  CategoriaUpdate,
} from '@/entities/admin/types'

interface CategoriaTree extends CategoriaAdminRead {
  hijos?: CategoriaTree[]
}

function flattenTree(nodes: CategoriaTree[]): CategoriaAdminRead[] {
  const result: CategoriaAdminRead[] = []
  function traverse(items: CategoriaTree[]) {
    for (const node of items) {
      result.push({ id: node.id, nombre: node.nombre, descripcion: node.descripcion, parent_id: node.parent_id, created_at: node.created_at })
      if (node.hijos?.length) traverse(node.hijos)
    }
  }
  traverse(nodes)
  return result
}

export const listarCategoriasAdmin = (): Promise<CategoriaAdminRead[]> =>
  api
    .get<CategoriaTree[]>('/categorias')
    .then((r) => flattenTree(r.data))

export const crearCategoria = (
  body: CategoriaCreate,
): Promise<CategoriaAdminRead> =>
  api
    .post<CategoriaAdminRead>('/categorias/', body)
    .then((r) => r.data)

export const actualizarCategoria = (
  id: number,
  body: CategoriaUpdate,
): Promise<CategoriaAdminRead> =>
  api
    .put<CategoriaAdminRead>(`/categorias/${id}`, body)
    .then((r) => r.data)

export const eliminarCategoria = (id: number): Promise<void> =>
  api.delete(`/categorias/${id}`).then(() => undefined)
