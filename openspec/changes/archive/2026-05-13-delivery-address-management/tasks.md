## 1. Model — Actualizar DireccionEntrega

- [x] 1.1 Modificar `backend/direcciones/model.py`: reemplazar `linea1`/`linea2` por campos granulares (`calle`, `numero`, `piso`, `departamento`, `provincia`) y agregar `deleted_at: Optional[datetime]`
- [x] 1.2 Verificar que la relación `usuario: "Usuario"` y `pedidos: list["Pedido"]` permanecen intactas en el modelo actualizado

## 2. Schemas — Actualizar DireccionEntrega

- [x] 2.1 Actualizar `DireccionEntregaCreate` en `backend/direcciones/schemas.py`: eliminar `usuario_id` del schema de creación (el `usuario_id` viene del token, no del body), reemplazar `linea1`/`linea2` por los campos granulares del modelo
- [x] 2.2 Actualizar `DireccionEntregaUpdate` en `backend/direcciones/schemas.py`: todos los campos opcionales, campos granulares en lugar de `linea1`/`linea2`
- [x] 2.3 Actualizar `DireccionEntregaRead` en `backend/direcciones/schemas.py`: incluir los nuevos campos granulares y `deleted_at`

## 3. Repository — Implementar DireccionEntregaRepository

- [x] 3.1 Implementar `DireccionEntregaRepository(BaseRepository[DireccionEntrega])` en `backend/direcciones/repository.py`
- [x] 3.2 Agregar método `list_by_usuario(usuario_id: int) -> list[DireccionEntrega]`: filtra `usuario_id == usuario_id` AND `deleted_at IS NULL`
- [x] 3.3 Agregar método `unset_principal(usuario_id: int) -> None`: ejecuta `UPDATE direccionentrega SET es_principal=False WHERE usuario_id=:uid AND deleted_at IS NULL` via bulk statement
- [x] 3.4 Agregar método `get_active(direccion_id: int) -> DireccionEntrega | None`: busca por PK con filtro `deleted_at IS NULL`

## 4. Service — Implementar DireccionEntregaService

- [x] 4.1 Crear `backend/direcciones/service.py` e implementar función helper privada `_get_direccion_owned(uow, direccion_id, usuario_id) -> DireccionEntrega`: lanza `NotFoundException` si no existe/eliminada, lanza `ForbiddenException` si `usuario_id` no coincide
- [x] 4.2 Implementar `crear(uow, body: DireccionEntregaCreate, usuario_id: int) -> DireccionEntrega`: crea la dirección con `usuario_id` del parámetro (no del body)
- [x] 4.3 Implementar `listar(uow, usuario_id: int) -> list[DireccionEntrega]`: delega a `repo.list_by_usuario(usuario_id)`
- [x] 4.4 Implementar `actualizar(uow, direccion_id: int, body: DireccionEntregaUpdate, usuario_id: int) -> DireccionEntrega`: usa `_get_direccion_owned`, aplica campos no-None del body, delega a `repo.update()`
- [x] 4.5 Implementar `eliminar(uow, direccion_id: int, usuario_id: int) -> None`: usa `_get_direccion_owned`, delega a `repo.delete()` (el BaseRepository maneja el soft delete via `deleted_at`)
- [x] 4.6 Implementar `marcar_principal(uow, direccion_id: int, usuario_id: int) -> DireccionEntrega`: usa `_get_direccion_owned`, llama `repo.unset_principal(usuario_id)`, luego `direccion.es_principal = True` + `repo.update(direccion)`

## 5. Router — Implementar endpoints

- [x] 5.1 Crear `backend/direcciones/router.py` con `router = APIRouter()` y `_get_uow()` local con `DireccionEntregaRepository` registrado (patrón de `categorias/router.py`)
- [x] 5.2 Implementar `POST /` → `crear_direccion`: requiere `get_current_user`, llama `service.crear(uow, body, current_user.id)`, responde 201 con `DireccionEntregaRead`
- [x] 5.3 Implementar `GET /` → `listar_direcciones`: requiere `get_current_user`, llama `service.listar(uow, current_user.id)`, responde 200 con `list[DireccionEntregaRead]`
- [x] 5.4 Implementar `PUT /{id}` → `actualizar_direccion`: requiere `get_current_user`, llama `service.actualizar(uow, id, body, current_user.id)`, responde 200 con `DireccionEntregaRead`
- [x] 5.5 Implementar `DELETE /{id}` → `eliminar_direccion`: requiere `get_current_user`, llama `service.eliminar(uow, id, current_user.id)`, commit, responde 204 No Content
- [x] 5.6 Implementar `PATCH /{id}/principal` → `marcar_principal_direccion`: requiere `get_current_user`, llama `service.marcar_principal(uow, id, current_user.id)`, commit, responde 200 con `DireccionEntregaRead`

## 6. Registrar Router en API v1

- [x] 6.1 Agregar import `from backend.direcciones.router import router as direcciones_router` en `backend/api/v1/router.py`
- [x] 6.2 Agregar `(direcciones_router, "/usuarios/me/direcciones", "direcciones")` a la lista `sub_routers`

## 7. Migración Alembic

- [x] 7.1 Ejecutar `alembic revision --autogenerate -m "alter_direccionentrega_granular_fields_and_soft_delete"` para generar la migración automática
- [x] 7.2 Revisar y ajustar manualmente el archivo generado: renombrar `linea1` → `calle`, agregar `numero`, `piso`, `departamento`, `provincia`, `deleted_at`; quitar `linea2`
- [x] 7.3 Ejecutar `alembic upgrade head` y verificar que la tabla `direccionentrega` tiene la estructura correcta

## 8. Verificación

- [x] 8.1 Verificar que `GET /api/v1/usuarios/me/direcciones` devuelve 401 sin token
- [x] 8.2 Verificar que `POST /api/v1/usuarios/me/direcciones` crea y devuelve la dirección con 201
- [x] 8.3 Verificar que `PATCH /{id}/principal` actualiza `es_principal` atómicamente para todas las direcciones del usuario
- [x] 8.4 Verificar que `DELETE /{id}` aplica soft delete y la dirección no aparece en `GET /`
- [x] 8.5 Verificar que `PUT /{id}` con `{id}` de otro usuario devuelve 403
