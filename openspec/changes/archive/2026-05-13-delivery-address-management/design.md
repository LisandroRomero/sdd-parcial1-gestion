## Context

El módulo `backend/direcciones/` existe parcialmente: tiene `model.py` con `DireccionEntrega` (usando `linea1`/`linea2` en lugar de los campos granulares de la spec) y `schemas.py` básico. El `repository.py`, `service.py` y `router.py` están vacíos (1 línea). No hay ningún endpoint expuesto.

La spec v5.0 define `DireccionEntrega` con campos granulares: `calle`, `numero`, `piso`, `departamento`, `ciudad`, `provincia`, `codigo_postal`. El modelo actual usa `linea1`/`linea2` que no siguen la spec. Se requiere una migración que actualice el schema de la tabla.

El módulo ya existe en `backend/api/v1/router.py` como import pendiente (no está incluido todavía). El patrón de referencia es `backend/categorias/` que usa UoW local por router (en lugar de el UoW global de `core/dependencies.py`).

## Goals / Non-Goals

**Goals:**
- Alinear `DireccionEntrega` con la spec v5.0 (campos granulares + `deleted_at`)
- Implementar los 5 endpoints de gestión de direcciones bajo `/api/v1/usuarios/me/direcciones`
- Garantizar ownership: un usuario solo puede ver/modificar/eliminar sus propias direcciones
- Implementar la regla de principal única: al marcar una dirección como principal, las demás del mismo usuario quedan `es_principal=False`
- Soft delete via `deleted_at` (aprovechando `BaseRepository.delete()` que ya maneja esto)
- Registrar el router en `backend/api/v1/router.py`
- Crear migración Alembic para el cambio de schema

**Non-Goals:**
- Endpoint para que ADMIN gestione direcciones de otros usuarios (no requerido en spec)
- Validación avanzada de bloqueo de eliminación de dirección principal con pedidos activos (se implementa soft delete libre)
- Geocodificación o validación de dirección contra un servicio externo
- Paginación en el listado (las direcciones por usuario son pocas en la práctica)

## Decisions

### 1. Campos del modelo: reemplazar `linea1`/`linea2` por campos granulares

**Decisión:** Migrar el modelo a campos explícitos: `calle`, `numero`, `piso` (opcional), `departamento` (opcional), `ciudad`, `provincia`, `codigo_postal`.

**Por qué:** La spec v5.0 define campos granulares. El modelo actual con `linea1`/`linea2` es una simplificación que no sigue la spec y dificultaría búsquedas por ciudad/provincia en el futuro.

**Alternativa considerada:** Mantener `linea1`/`linea2` y renombrarlos — descartada porque no respeta la spec y difiere del ERD v5.

### 2. Agregar `deleted_at` para soft delete

**Decisión:** Agregar `deleted_at: Optional[datetime]` al modelo.

**Por qué:** `BaseRepository.delete()` ya maneja soft delete automáticamente si el modelo tiene `deleted_at`. Cero código extra en el repository o service. El patrón ya existe en `Categoria` y `Usuario`.

### 3. UoW local por router (mismo patrón que categorias)

**Decisión:** El router de direcciones define su propio `_get_uow()` con `DireccionEntregaRepository` registrado, en lugar de modificar `core/dependencies.py`.

**Por qué:** Cada módulo es self-contained. El `get_uow()` global de `core/dependencies.py` no registra repositorios de todos los módulos — cada router gestiona su propio UoW. Este es el patrón establecido en `categorias/router.py`.

**Alternativa considerada:** Centralizar en `core/dependencies.py` — descartada porque requeriría importar todos los repos en core (viola el sentido de flujo) y modificaría un módulo compartido sin necesidad.

### 4. Regla de principal única en el service

**Decisión:** Al llamar `marcar_principal(uow, direccion_id, usuario_id)`, el service ejecuta:
1. Verificar ownership (404 si no existe, 403 si no es del usuario)
2. Ejecutar `UPDATE` con `es_principal=False` para todas las direcciones del usuario
3. Ejecutar `UPDATE` con `es_principal=True` para la dirección target
4. Commit vía UoW

**Por qué:** La atomicidad se garantiza por el UoW que envuelve ambas operaciones en la misma transacción. El service lanza `ForbiddenException` si el usuario no es el dueño.

### 5. Ownership check centralizado en el service

**Decisión:** El service expone una función `_get_direccion_owned(uow, direccion_id, usuario_id)` que:
- Busca la dirección (incluye `deleted_at IS NULL` vía `BaseRepository`)
- 404 si no existe
- 403 si `usuario_id` no coincide con `direccion.usuario_id`

**Por qué:** Evitar duplicación del check en cada operación (update, delete, patch/principal). Principio DRY.

### 6. Endpoints bajo `/usuarios/me/direcciones`

**Decisión:** El router de direcciones se incluye como subrouter del router de usuarios en `backend/api/v1/router.py` con prefijo `/usuarios/me/direcciones`.

**Por qué:** Los endpoints son recursos del usuario autenticado. La URL `/me/direcciones` es REST-idiomatic para "recursos propios del usuario actual".

## Risks / Trade-offs

- **Migración destructiva de campos**: Reemplazar `linea1`/`linea2` por campos granulares es una migración de renombre/adición. Si hay datos en producción con `linea1`/`linea2`, hay que mapearlos. Mitigación: en este contexto de desarrollo la BD está vacía, pero la migración debe incluir comentario de la transformación.

- **Sin paginación en listado**: El endpoint `GET /me/direcciones` devuelve todas las direcciones activas del usuario. Mitigación: los usuarios raramente tienen más de 5-10 direcciones guardadas; si se vuelve un problema, agregar paginación en iteración posterior.

- **soft delete no bloquea pedidos activos**: Simplificamos eliminando la regla avanzada "no eliminar principal con pedidos activos". Mitigación: puede agregarse en Epic 4 cuando se implemente el módulo de pedidos completo.

## Migration Plan

1. Crear migración Alembic: `alembic revision --autogenerate -m "alter_direccionentrega_add_fields"` — ajustar manualmente para renombrar `linea1`→`calle` y agregar los campos faltantes con sus constraints.
2. Ejecutar `alembic upgrade head` en el entorno de desarrollo.
3. Incluir el router en `backend/api/v1/router.py`.
4. Verificar endpoints con la colección de Postman o `httpie` contra `localhost:8000`.

**Rollback:** `alembic downgrade -1` revierte la migración. El router puede removerse del `api/v1/router.py`.

## Open Questions

- ¿Se necesita un endpoint de lectura individual `GET /me/direcciones/{id}`? La spec de US-024 a US-028 no lo menciona explícitamente. Por ahora se omite; fácil de agregar si se requiere.
- ¿El campo `provincia` debe ser un enum (lista de provincias argentinas) o string libre? Por simplidad y flexibilidad se implementa como string; la validación puede endurecerse luego.
