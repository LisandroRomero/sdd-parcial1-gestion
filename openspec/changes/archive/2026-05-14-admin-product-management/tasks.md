## 1. Backend — Corregir guards de productos

- [x] 1.1 En `backend/productos/router.py`, cambiar los 3 endpoints que tienen solo `require_role("ADMIN")` para incluir también `"STOCK"`:
  - `POST /` (crear_producto) → `require_role("ADMIN", "STOCK")`
  - `PUT /{id}` (actualizar_producto) → `require_role("ADMIN", "STOCK")`
  - `DELETE /{id}` (eliminar_producto) → `require_role("ADMIN", "STOCK")`

## 2. Frontend — Tipos de mutación

- [x] 2.1 En `frontend/src/entities/producto/types.ts`, agregar interfaces de mutación:
  - `ProductoCreate` (codigo_sku, nombre, descripcion?, precio_base: string, stock_cantidad, disponible, imagen_url?, categoria_ids: number[])
  - `ProductoUpdate` (todos opcionales, mismos campos)
  - `StockUpdate` (stock_cantidad: number)
  - `DisponibilidadUpdate` (disponible: boolean)

- [x] 2.2 En `frontend/src/entities/admin/types.ts`, agregar interfaces para categorías e ingredientes:
  - `CategoriaAdminRead` (id, nombre, descripcion?: string, parent_id?: number, created_at?: string)
  - `CategoriaCreate` (nombre: string, descripcion?: string, parent_id?: number)
  - `CategoriaUpdate` (todos opcionales)
  - `CategoriaPaginado` (items: CategoriaAdminRead[], total: number)
  - `IngredienteAdminRead` (id, nombre, es_alergeno: boolean, created_at?: string)
  - `IngredienteCreate` (nombre: string, es_alergeno: boolean)
  - `IngredienteUpdate` (nombre?: string, es_alergeno?: boolean)
  - `IngredientePaginado` (items: IngredienteAdminRead[], total: number)

## 3. Frontend — API clients admin

- [x] 3.1 Crear `frontend/src/features/admin/api/adminProductosApi.ts` con las funciones:
  - `crearProducto(body: ProductoCreate)` → `POST /productos/`
  - `actualizarProducto(id: number, body: ProductoUpdate)` → `PUT /productos/{id}`
  - `eliminarProducto(id: number)` → `DELETE /productos/{id}`
  - `actualizarStockAdmin(id: number, body: StockUpdate)` → `PATCH /productos/{id}/stock`
  - `cambiarDisponibilidad(id: number, body: DisponibilidadUpdate)` → `PATCH /productos/{id}/disponibilidad`

- [x] 3.2 Crear `frontend/src/features/admin/api/adminCategoriasApi.ts`:
  - `listarCategoriasAdmin()` → `GET /categorias` (returns CategoriaPaginado)
  - `crearCategoria(body: CategoriaCreate)` → `POST /categorias/`
  - `actualizarCategoria(id: number, body: CategoriaUpdate)` → `PUT /categorias/{id}`
  - `eliminarCategoria(id: number)` → `DELETE /categorias/{id}`

- [x] 3.3 Crear `frontend/src/features/admin/api/adminIngredientesApi.ts`:
  - `listarIngredientesAdmin(page?, size?)` → `GET /ingredientes` (returns IngredientePaginado)
  - `crearIngrediente(body: IngredienteCreate)` → `POST /ingredientes/`
  - `actualizarIngrediente(id: number, body: IngredienteUpdate)` → `PUT /ingredientes/{id}`
  - `eliminarIngrediente(id: number)` → `DELETE /ingredientes/{id}`

## 4. Frontend — Hooks de mutación

- [x] 4.1 Crear hooks de productos en `frontend/src/features/admin/hooks/`:
  - `useCrearProducto.ts` — useMutation + invalidate `['productos']`
  - `useActualizarProducto.ts` — useMutation + invalidate
  - `useEliminarProducto.ts` — useMutation + invalidate
  - `useActualizarStock.ts` — useMutation + invalidate
  - `useCambiarDisponibilidadAdmin.ts` — useMutation + invalidate

- [x] 4.2 Crear hooks de categorías en `frontend/src/features/admin/hooks/`:
  - `useListarCategoriasAdmin.ts` — useQuery sobre `listarCategoriasAdmin`
  - `useCrearCategoria.ts` — useMutation + invalidate `['categorias-admin']`
  - `useActualizarCategoria.ts` — useMutation + invalidate
  - `useEliminarCategoria.ts` — useMutation + invalidate

- [x] 4.3 Crear hooks de ingredientes en `frontend/src/features/admin/hooks/`:
  - `useListarIngredientesAdmin.ts` — useQuery sobre `listarIngredientesAdmin` con queryKey `['ingredientes-admin']`
  - `useCrearIngrediente.ts` — useMutation + invalidate
  - `useActualizarIngrediente.ts` — useMutation + invalidate
  - `useEliminarIngrediente.ts` — useMutation + invalidate

## 5. Frontend — Páginas admin

- [x] 5.1 Crear `frontend/src/pages/admin/AdminProductosPage.tsx`:
  - Usar `useProductos` existente de `@/features/catalogo/hooks/useProductos` para el listado (o hacer llamada directa)
  - Tabla con columnas: nombre, SKU, precio (ARS), stock, disponible (badge/toggle), categorías, acciones
  - Botón "Nuevo producto" → modal con `ProductoCreate` form (codigo_sku, nombre, precio_base, stock_cantidad, categoria_ids multiselect, descripcion, disponible)
  - Acciones por fila: "Editar" (modal), toggle disponibilidad (botón), "Stock" (input inline), "Eliminar" (confirm dialog)
  - Mostrar errores del backend en el modal/toast

- [x] 5.2 Crear `frontend/src/pages/admin/AdminCategoriasPage.tsx`:
  - Usar `useListarCategoriasAdmin` para el listado
  - Tabla con columnas: nombre, descripción, categoría padre, fecha, acciones
  - Botón "Nueva categoría" → modal con CategoriaCreate form (nombre, descripcion, parent_id select)
  - Acciones por fila: "Editar" (modal), "Eliminar" (confirm dialog con nota del error si tiene productos)

- [x] 5.3 Crear `frontend/src/pages/admin/AdminIngredientesPage.tsx`:
  - Usar `useListarIngredientesAdmin` para el listado
  - Tabla con columnas: nombre, es alergeno (badge), fecha, acciones
  - Botón "Nuevo ingrediente" → modal con IngredienteCreate form (nombre, es_alergeno checkbox)
  - Acciones por fila: "Editar" (modal), "Eliminar" (confirm dialog)

## 6. Frontend — Routing

- [x] 6.1 En `frontend/src/app/router.tsx`, agregar dentro del grupo AdminRoute:
  - `AdminProductosPage` lazy import y ruta `productos`
  - `AdminCategoriasPage` lazy import y ruta `categorias`
  - `AdminIngredientesPage` lazy import y ruta `ingredientes`
