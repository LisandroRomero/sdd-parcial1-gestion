## Context

El módulo `backend/productos/` implementa actualmente CRUD completo (Epic 2.3) y la asociación producto-ingrediente (Epic 2.4). Todos sus endpoints requieren autenticación con roles ADMIN o STOCK. No existe ningún endpoint de lectura pública. El router está registrado en `backend/api/v1/router.py` con prefijo `/productos`.

La capa de datos ya contiene toda la información necesaria:
- `productos` — campos `deleted_at`, `disponible`, `precio_base`, `nombre`, `descripcion`
- `producto_categorias` — tabla pivote con `es_principal`
- `producto_ingredientes` — tabla pivote con `cantidad`, `unidad`, `es_removible`
- `ingredientes` — campo `es_alergeno`
- `categorias` — jerarquía con `parent_id`

## Goals / Non-Goals

**Goals:**
- Exponer `GET /api/v1/productos` y `GET /api/v1/productos/{id}` sin autenticación requerida.
- Soportar filtros: `categoria_id`, `disponible`, `precio_min`, `precio_max`, `busqueda` (ILIKE en nombre + descripcion), `tiene_alergenos`.
- Retornar detalle enriquecido con categorías e ingredientes (incluyendo `es_alergeno` por ingrediente y `tiene_alergenos` derivado).
- No romper ningún endpoint ADMIN/STOCK existente.

**Non-Goals:**
- Paginación por cursor — usar offset/page clásico (consistente con epics anteriores).
- Caching de respuestas (Redis) — fuera del alcance de este epic.
- Exponer productos con `deleted_at IS NOT NULL` al público — siempre filtrados.
- Endpoint de categorías públicas — ya existe en `backend/categorias/router.py`.

## Decisions

### D1: Extender el router existente, no crear uno nuevo

**Decision:** agregar los dos endpoints públicos directamente en `backend/productos/router.py`, antes de los endpoints protegidos.

**Rationale:** el prefijo `/api/v1/productos` ya es el correcto. Crear un router separado (`public_router`) implicaría registrarlo en `backend/api/v1/router.py` con el mismo prefijo, generando confusión de ownership. Al poner los endpoints públicos primero en el mismo archivo, FastAPI los evalúa antes que los protegidos — sin colisiones de ruta porque los públicos usan exactamente `GET /` y `GET /{id}`, mientras que los protegidos usan `POST /`, `PUT /{id}`, `PATCH /{id}/...`, `DELETE /{id}`.

**Alternative considered:** router separado `public_router` montado en `/productos`. Descartado — complejidad innecesaria sin beneficio.

### D2: `ProductoFiltros` como clase de query params (no params individuales)

**Decision:** declarar `ProductoFiltros` como `BaseModel` con todos los query params y usarlo con `Depends(ProductoFiltros)` en el endpoint.

**Rationale:** FastAPI soporta modelos Pydantic como dependency para query params. Agrupa la validación en un lugar, permite re-uso en tests y en otros endpoints si es necesario. Consistente con el patrón de otros proyectos FastAPI modernos.

```python
class ProductoFiltros(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    categoria_id: Optional[int] = None
    disponible: Optional[bool] = None
    precio_min: Optional[Decimal] = None
    precio_max: Optional[Decimal] = None
    busqueda: Optional[str] = None
    tiene_alergenos: Optional[bool] = None
```

**Alternative considered:** params individuales en la firma del endpoint. Más verboso, sin ventajas.

### D3: JOIN en SQL para filtro de alérgenos, no post-processing en Python

**Decision:** el filtro `tiene_alergenos` se resuelve en la query SQL con EXISTS/subquery.

**Rationale:** filtrar alérgenos en Python requeriría traer TODOS los productos y luego descartar, lo que es ineficiente. Con EXISTS en SQL, el motor descarta filas antes de paginar.

```sql
-- tiene_alergenos = True
WHERE EXISTS (
  SELECT 1 FROM producto_ingredientes pi
  JOIN ingredientes i ON pi.ingrediente_id = i.id
  WHERE pi.producto_id = producto.id
    AND i.es_alergeno = TRUE
    AND i.deleted_at IS NULL
)

-- tiene_alergenos = False
WHERE NOT EXISTS (...)
```

### D4: `ProductoDetalleRead` como schema separado (no heredar de `ProductoRead`)

**Decision:** `ProductoDetalleRead` hereda de `ProductoRead` y agrega los campos de relaciones.

**Rationale:** herencia directa reutiliza todos los campos de `ProductoRead` sin duplicación. El campo `tiene_alergenos: bool` es derivado y calculado en el service (no almacenado en BD), garantizando que siempre esté sincronizado.

```python
class ProductoDetalleRead(ProductoRead):
    categorias: list[CategoriaRead] = []
    ingredientes: list[ProductoIngredienteRead] = []
    tiene_alergenos: bool = False
```

### D5: Carga de relaciones en repositorio con query explícita (no lazy loading)

**Decision:** `get_detalle_public(id)` en el repositorio hace un select explícito de `ProductoCategoria` + `Categoria` y `ProductoIngrediente` + `Ingrediente`, sin depender de lazy loading de SQLModel.

**Rationale:** SQLModel con SQLite/Postgres en modo síncrono puede triggear lazy loads inesperados si se accede a relaciones fuera de la sesión. Cargar explícitamente en el repo garantiza que todo está disponible antes de cerrar la sesión. Patrón ya establecido en `IngredienteRepository.listar_por_producto()`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| N+1 en `list_public()` si se cargan relaciones por producto | El endpoint de listado NO incluye ingredientes/categorías en los items — solo `ProductoRead` plano. Las relaciones solo se cargan en el endpoint de detalle. |
| El campo `disponible=None` en el listado público vs. ADMIN | Por defecto (si `disponible` no se pasa), el endpoint público filtra `disponible=True`. Solo un ADMIN autenticado puede pasar `disponible=false` — la spec aclara este comportamiento. |
| Búsqueda ILIKE lenta en tablas grandes | Fuera del alcance; se puede agregar índice `GIN trgm` en el futuro si es necesario. |
| `precio_min > precio_max` | Validado en `ProductoFiltros` con `model_validator`. |

## Migration Plan

1. Agregar schemas en `backend/productos/schemas.py`.
2. Agregar métodos en `backend/productos/repository.py`.
3. Agregar funciones en `backend/productos/service.py`.
4. Agregar endpoints en `backend/productos/router.py` (antes de los endpoints protegidos).
5. No hay migraciones de BD.
6. No hay cambios en `backend/api/v1/router.py` — el router de productos ya está registrado.

**Rollback:** revertir los cambios en los 4 archivos afectados. No hay estado persistente nuevo.

## Open Questions

- ¿Se debe exponer `stock_cantidad` en el listado público? Por spec SDD v5.0 se expone — los clientes pueden ver si hay stock. Incluido en `ProductoRead` (ya tiene el campo).
- ¿Ordenamiento por defecto? Spec no lo define; se usará `id ASC` como tiebreaker determinístico.
