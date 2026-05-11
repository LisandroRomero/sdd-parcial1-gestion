## 1. Schemas

- [x] 1.1 Agregar `CategoriaTree` en `backend/categorias/schemas.py` — Pydantic v2 con `hijos: list["CategoriaTree"] = []` y `model_rebuild()`
- [x] 1.2 Agregar validación `@field_validator("parent_id")` en `CategoriaCreate` / `CategoriaUpdate` para rechazar `parent_id == id` (auto-referencia directa)

## 2. Repository

- [x] 2.1 Crear `CategoriaRepository(BaseRepository[Categoria])` en `backend/categorias/repository.py`
- [x] 2.2 Implementar `get_tree() -> list[dict]` con CTE recursiva (raw SQL `text()`) que retorna filas planas ordenadas por `depth`
- [x] 2.3 Implementar `get_by_id_active(id: int) -> Categoria | None` — filtra `deleted_at IS NULL`
- [x] 2.4 Implementar `exists_name_at_level(nombre: str, parent_id: int | None, exclude_id: int | None) -> bool` — validación de nombre duplicado en mismo nivel
- [x] 2.5 Implementar `has_ancestor_cycle(target_id: int, new_parent_id: int) -> bool` — CTE de ancestros para detección de ciclos
- [x] 2.6 Implementar `count_active_products(categoria_id: int) -> int` — cuenta productos activos asociados vía `ProductoCategoria`
- [x] 2.7 Implementar `count_active_hijos(categoria_id: int) -> int` — cuenta subcategorías activas directas

## 3. Service

- [x] 3.1 Crear `CategoriaService` en `backend/categorias/service.py`
- [x] 3.2 Implementar `crear(uow, data: CategoriaCreate) -> Categoria` — valida nombre duplicado, crea vía UoW
- [x] 3.3 Implementar `listar_arbol(uow) -> list[CategoriaTree]` — llama `get_tree()` y construye árbol anidado en Python con dict-index
- [x] 3.4 Implementar `actualizar(uow, id: int, data: CategoriaUpdate) -> Categoria` — valida existencia, auto-referencia, ciclos y nombre duplicado; actualiza vía UoW
- [x] 3.5 Implementar `eliminar(uow, id: int) -> None` — valida existencia, productos activos y subcategorías activas; aplica soft delete vía UoW

## 4. Router

- [x] 4.1 Crear `backend/categorias/router.py` con `APIRouter()`
- [x] 4.2 `POST /` — `response_model=CategoriaRead`, roles ADMIN/STOCK, llama `CategoriaService.crear()`
- [x] 4.3 `GET /` — `response_model=list[CategoriaTree]`, público (sin autenticación), llama `CategoriaService.listar_arbol()`
- [x] 4.4 `PUT /{id}` — `response_model=CategoriaRead`, roles ADMIN/STOCK, llama `CategoriaService.actualizar()`
- [x] 4.5 `DELETE /{id}` — status `204`, roles ADMIN/STOCK, llama `CategoriaService.eliminar()`

## 5. Registro e Integración

- [x] 5.1 Registrar `categorias_router` en `backend/api/v1/router.py` con prefijo `/categorias` y tag `"categorias"`
- [x] 5.2 Verificar que `backend/core/models.py` importa el modelo `Categoria` (para que SQLModel lo registre en el mapper)

## 6. Verificación

- [x] 6.1 Levantar backend y confirmar que `GET /api/v1/categorias` retorna `HTTP 200` con `[]` en DB vacía
- [x] 6.2 `POST /api/v1/categorias` con token ADMIN → `HTTP 201` con categoría raíz
- [x] 6.3 `POST /api/v1/categorias` con `parent_id` válido → `HTTP 201` con subcategoría
- [x] 6.4 Crear ciclo: hacer `PUT` con `parent_id` que genera ciclo → `HTTP 409`
- [x] 6.5 `DELETE /api/v1/categorias/{id}` en categoría vacía → `HTTP 204`
- [x] 6.6 `DELETE` en categoría con subcategorías activas → `HTTP 409`
- [x] 6.7 `GET /api/v1/categorias` retorna árbol anidado correcto con múltiples niveles
- [x] 6.8 Confirmar en Swagger (`/docs`) que los 4 endpoints aparecen con sus `response_model`
