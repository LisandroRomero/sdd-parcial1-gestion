## Context

El módulo `ingredientes` ya tiene el modelo `ProductoIngrediente` (tabla pivote) con campos `producto_id`, `ingrediente_id` y `es_removible`. Sin embargo la tabla carece de `cantidad` y `unidad`, y no existen endpoints REST para gestionar la asociación. Los módulos `productos` e `ingredientes` están completamente implementados con el patrón `Router → Service → UoW → Repository → Model`.

La arquitectura del proyecto usa un `UnitOfWork` con un `_ReposRegistry` de acceso lazy: en cada router se registran los repositorios necesarios para esa request. Esto permite que un único endpoint (en `productos/router.py`) use a la vez `ProductoRepository` e `IngredienteRepository` sin acoplamiento entre módulos.

## Goals / Non-Goals

**Goals:**
- Agregar `cantidad` (float, nullable) y `unidad` (string 20, nullable) al modelo `ProductoIngrediente` y generar la migración Alembic correspondiente
- Implementar `POST /api/v1/productos/{id}/ingredientes`, `GET /api/v1/productos/{id}/ingredientes` y `DELETE /api/v1/productos/{id}/ingredientes/{ingrediente_id}`
- Agregar los schemas Pydantic `ProductoIngredienteCreate`, `ProductoIngredienteRead`, `ProductoIngredienteListResponse` en `backend/ingredientes/schemas.py`
- Agregar métodos de asociación en `backend/ingredientes/repository.py`: `agregar_a_producto`, `listar_por_producto`, `remover_de_producto`, `existe_asociacion`
- Agregar funciones de negocio en `backend/ingredientes/service.py`: `asociar`, `listar_ingredientes_producto`, `desasociar`
- Registrar los nuevos endpoints en `backend/productos/router.py` con un `_get_uow` extendido que registre ambos repositorios

**Non-Goals:**
- No se implementa frontend para esta feature en este change
- No se modifica el comportamiento de los endpoints CRUD de ingredientes ya implementados
- No se implementa paginación para la lista de ingredientes de un producto (la lista se devuelve completa; un producto raramente tiene más de ~30 ingredientes)
- No se implementa la eliminación en cascada al borrar un producto (ya manejado por FK con `ON DELETE CASCADE` a nivel de BD, según el diseño actual)

## Decisions

### D1 — Los nuevos endpoints viven en `productos/router.py`, no en `ingredientes/router.py`

**Por qué:** Los endpoints son sub-recursos del producto (`/productos/{id}/ingredientes`). Colocarlos en el router de productos respeta la semántica REST y la estructura Feature-First del proyecto.

**Alternativa rechazada:** Crear un router propio `producto_ingredientes/router.py`. Agrega un módulo extra para solo 3 endpoints, fragmenta la navegación y no aporta encapsulamiento real dado que el dominio dueño es el producto.

### D2 — La lógica de negocio de la asociación vive en `ingredientes/service.py`

**Por qué:** El service de ingredientes ya conoce el modelo `ProductoIngrediente` (vive en `ingredientes/model.py`). Agregar funciones de asociación en el mismo módulo evita crear dependencia cruzada entre módulos. El router de productos solo importa las funciones del service, no el módulo completo.

**Alternativa rechazada:** Colocar la lógica en `productos/service.py`. Implicaría que `productos/service.py` importa modelos de `ingredientes/`, creando acoplamiento en la dirección equivocada.

### D3 — El `_get_uow` del router de productos se extiende para registrar ambos repositorios

**Por qué:** El `UnitOfWork` del proyecto soporta múltiples repositorios en la misma transacción vía `_ReposRegistry`. El endpoint necesita verificar que el producto existe (ProductoRepository) y que el ingrediente existe (IngredienteRepository) en la misma transacción atómica.

**Alternativa rechazada:** Inyectar dos UoW separados. Rompe la atomicidad de la transacción; si el insert falla a mitad, no hay forma de rollback coordinado.

### D4 — Asociación duplicada retorna 409, no upsert silencioso

**Por qué:** El upsert silencioso oculta errores del cliente (enviar el mismo ingrediente dos veces es casi siempre un bug de integración). El 409 con código `PRODUCTO_INGREDIENTE_DUPLICADO` da feedback claro al consumidor de la API.

**Alternativa rechazada:** Upsert (UPDATE si existe, INSERT si no). Podría tener sentido para actualizar `cantidad`/`unidad`, pero complica la semántica del endpoint POST. Si se necesita actualizar, se puede agregar un `PATCH` en el futuro.

### D5 — La migración agrega columnas con `ALTER TABLE`, no recrea la tabla

**Por qué:** `producto_ingredientes` puede tener datos existentes. Recrear la tabla implica pérdida de datos. Las columnas `cantidad` y `unidad` son nullable, por lo que el `ALTER TABLE ADD COLUMN` no requiere valor por defecto ni bloqueos largos.

## Risks / Trade-offs

- **[Riesgo] Modelo `ProductoIngrediente` ya puede tener filas en producción sin `cantidad`/`unidad`** → Mitigación: las columnas son nullable con `default=None`; la migración Alembic usa `ALTER TABLE ADD COLUMN` sin `NOT NULL`. Filas existentes quedan con `NULL` en ambas columnas, lo que es semánticamente correcto.

- **[Riesgo] El campo `es_removible` en `ProductoIngrediente` no está en la especificación técnica del Integrador** → Mitigación: el campo ya existe en el modelo; se expone en `ProductoIngredienteRead` para no perder información. No se elimina en este change.

- **[Trade-off] Lista de ingredientes de un producto no está paginada** → Aceptado: los productos de food store tienen pocos ingredientes. Simplifica el contrato del endpoint `GET`. Si en el futuro hubiera productos con muchos ingredientes, se puede agregar paginación sin breaking change (agregar query params opcionales).

- **[Riesgo] Dos imports cruzados entre `productos/` e `ingredientes/`** → Mitigación: el router de productos importa *funciones* del service de ingredientes (no el módulo), y solo lo hace en el layer de Router. El service de productos no importa nada de ingredientes. Se mantiene el flujo unidireccional `Router → Service → UoW → Repository → Model`.

## Migration Plan

1. Modificar `backend/ingredientes/model.py` — agregar `cantidad: Optional[float]` y `unidad: Optional[str]` a `ProductoIngrediente`
2. Generar migración Alembic: `alembic revision --autogenerate -m "add_cantidad_unidad_to_producto_ingredientes"`
3. Revisar el script autogenerado para confirmar que solo agrega `ALTER TABLE producto_ingredientes ADD COLUMN cantidad FLOAT` y `ALTER TABLE producto_ingredientes ADD COLUMN unidad VARCHAR(20)`
4. Implementar schemas, repository methods, service functions y endpoints
5. Ejecutar `alembic upgrade head` en el ambiente de desarrollo

**Rollback:** `alembic downgrade -1` revierte el `ALTER TABLE`. No hay pérdida de datos ya que las columnas son nullable y simplemente se eliminan.

## Open Questions

- ¿Se necesita un endpoint `PATCH /api/v1/productos/{id}/ingredientes/{ingrediente_id}` para actualizar `cantidad`/`unidad` de una asociación existente? Por ahora se deja fuera del scope; el usuario puede hacer DELETE + POST si necesita cambiar los valores.
- ¿El flag `es_removible` tiene lógica de negocio activa en algún otro módulo (ej: pedidos)? Verificar antes de exponer en `ProductoIngredienteRead` para no crear contratos prematuros.
