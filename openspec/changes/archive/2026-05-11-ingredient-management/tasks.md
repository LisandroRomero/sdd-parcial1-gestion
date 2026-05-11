## 1. Modelo y Migración

- [x] 1.1 Agregar campo `deleted_at: Optional[datetime] = None` al modelo `Ingrediente` en `backend/ingredientes/model.py`
- [x] 1.2 Generar migración Alembic: `alembic revision --autogenerate -m "add_deleted_at_to_ingrediente"`
- [x] 1.3 Revisar la migración generada — debe contener solo `ADD COLUMN deleted_at TIMESTAMPTZ NULL`
- [x] 1.4 Aplicar migración: `alembic upgrade head` y verificar que no hay errores

## 2. Schemas

- [x] 2.1 Revisar `backend/ingredientes/schemas.py` — verificar que `IngredienteCreate`, `IngredienteUpdate` y `IngredienteRead` son correctos
- [x] 2.2 Agregar schema `IngredientePaginado` (o usar el patrón `PaginatedResponse` existente si hay uno en `core`) con campos `items`, `total`, `page`, `size`, `pages`

## 3. Repository

- [x] 3.1 Implementar `IngredienteRepository(BaseRepository[Ingrediente])` en `backend/ingredientes/repository.py`
- [x] 3.2 Implementar método `list_active(*, es_alergeno, skip, limit) -> tuple[list[Ingrediente], int]` con filtro opcional `es_alergeno` y `deleted_at IS NULL`
- [x] 3.3 Implementar método `get_by_id_active(id: int) -> Optional[Ingrediente]` — retorna None si `deleted_at IS NOT NULL`
- [x] 3.4 Implementar método `exists_by_nombre(nombre: str, exclude_id: Optional[int]) -> bool` — busca nombre activo excluyendo el ID propio (para update)

## 4. Service

- [x] 4.1 Implementar `IngredienteService` en `backend/ingredientes/service.py`
- [x] 4.2 Implementar `listar(uow, *, es_alergeno, page, size)` — delega a repo y construye respuesta paginada
- [x] 4.3 Implementar `crear(uow, data: IngredienteCreate)` — valida unicidad de nombre (409 si existe), luego crea con `uow.repos.ingredientes.create()`
- [x] 4.4 Implementar `actualizar(uow, id, data: IngredienteUpdate)` — 404 si no existe, 409 si nuevo nombre ya está en uso, persiste cambios con `uow.repos.ingredientes.update()`
- [x] 4.5 Implementar `eliminar(uow, id)` — 404 si no existe, aplica soft delete `ingrediente.deleted_at = datetime.now(tz=timezone.utc)` y llama `uow.repos.ingredientes.update()`

## 5. Router

- [x] 5.1 Implementar `GET /` en `backend/ingredientes/router.py` — público, query params `es_alergeno: Optional[bool]`, `page: int = 1`, `size: int = 20`
- [x] 5.2 Implementar `POST /` — requiere rol ADMIN o STOCK, body `IngredienteCreate`, response `201 IngredienteRead`
- [x] 5.3 Implementar `PUT /{id}` — requiere rol ADMIN o STOCK, body `IngredienteUpdate`, response `200 IngredienteRead`
- [x] 5.4 Implementar `DELETE /{id}` — requiere rol ADMIN o STOCK, response `204 No Content`
- [x] 5.5 Implementar `get_uow()` local en el router registrando `IngredienteRepository` en `uow.repos`

## 6. Integración

- [x] 6.1 Importar y registrar `ingredientes_router` en `backend/api/v1/router.py` con prefix `/ingredientes` y tag `ingredientes`

## 7. Verificación

- [x] 7.1 `GET /api/v1/ingredientes` retorna `200` con lista vacía sin errores
- [x] 7.2 `POST /api/v1/ingredientes` crea ingrediente y retorna `201` con ID y `created_at`
- [x] 7.3 `POST /api/v1/ingredientes` con nombre duplicado retorna `409`
- [x] 7.4 `PUT /api/v1/ingredientes/{id}` actualiza y retorna `200`
- [x] 7.5 `DELETE /api/v1/ingredientes/{id}` retorna `204` y el ingrediente no aparece en `GET`
- [x] 7.6 `GET /api/v1/ingredientes?es_alergeno=true` filtra correctamente
- [x] 7.7 `DELETE` con ID inexistente retorna `404`
