## Context

El módulo `backend/categorias/` tiene el modelo `Categoria` (FK auto-referencial, soft delete, timestamps) y schemas Pydantic base, pero `repository.py`, `service.py` y `router.py` están vacíos (1 línea cada uno). La tabla ya fue creada por la migración Alembic del change `0.3`. El UoW usa `_ReposRegistry` con `__getattr__` lazy-init — los repositorios se registran con `uow.repos.register(name, factory)`. El router v1 se ensambla en `backend/api/v1/router.py`.

## Goals / Non-Goals

**Goals:**
- Implementar los 4 endpoints de categorías: `POST /api/v1/categorias`, `GET /api/v1/categorias` (árbol), `PUT /api/v1/categorias/{id}`, `DELETE /api/v1/categorias/{id}`.
- CTE recursiva para construir el árbol jerárquico en una sola query.
- Validación de ciclos en `PUT` (CTE de ancestros).
- Soft delete con validación de productos activos (RN-CA03).
- Registrar el repositorio en UoW e incluir el router en `api/v1/router.py`.

**Non-Goals:**
- Asociación producto-categoría (change 2.3).
- Frontend / panel admin (change 7.3).
- Paginación del árbol (árbol completo en v1).
- Cache de la respuesta jerárquica.

## Decisions

### 1. CTE recursiva con SQLAlchemy `text()`

**Decisión:** query raw SQL con `text()` para el árbol y la detección de ciclos.

**Rationale:** SQLAlchemy ORM no soporta CTEs recursivas de forma nativa con `selectin_load` en self-joins. Una alternativa sería cargar todas las categorías y construir el árbol en Python, pero eso implica múltiples queries N+1 con lazy loading o un carga total sin filtrar deleted_at. Raw SQL CTE es una sola query, legible y alineada con el patrón de la spec (`CTE recursiva` mencionada explícitamente en el Integrador.txt).

**Árbol completo (`GET /categorias`):**
```sql
WITH RECURSIVE cat_tree AS (
    SELECT id, nombre, descripcion, parent_id, 0 AS depth
    FROM categoria
    WHERE parent_id IS NULL AND deleted_at IS NULL
  UNION ALL
    SELECT c.id, c.nombre, c.descripcion, c.parent_id, ct.depth + 1
    FROM categoria c
    JOIN cat_tree ct ON c.parent_id = ct.id
    WHERE c.deleted_at IS NULL
)
SELECT * FROM cat_tree ORDER BY depth, nombre;
```

**Detección de ciclos (`PUT` con nuevo `parent_id`):**
```sql
WITH RECURSIVE ancestors AS (
    SELECT id, parent_id FROM categoria WHERE id = :new_parent_id
  UNION ALL
    SELECT c.id, c.parent_id FROM categoria c JOIN ancestors a ON c.id = a.parent_id
    WHERE c.deleted_at IS NULL
)
SELECT id FROM ancestors WHERE id = :target_id;
```
Si retorna filas → hay ciclo → `HTTP 409`.

### 2. Construcción del árbol en Python después de la CTE

**Decisión:** la CTE retorna filas planas; el service construye el árbol en Python con un dict-index.

**Rationale:** Es más simple y performante que múltiples CTEs anidadas. Con el resultado plano ordenado por `depth`, una sola pasada O(n) con un dict `{id: nodo}` construye el árbol. Alternativa: múltiples CTEs o subqueries correlacionadas — más complejas sin beneficio real.

### 3. Schema `CategoriaTree` recursivo

**Decisión:** nuevo schema Pydantic con campo `hijos: list["CategoriaTree"]` y `model_rebuild()`.

```python
class CategoriaTree(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    hijos: list["CategoriaTree"] = []
    model_config = ConfigDict(from_attributes=True)

CategoriaTree.model_rebuild()
```

**Rationale:** El frontend necesita el árbol anidado para renderizar el selector jerárquico. Una lista plana con `parent_id` obligaría al frontend a construir el árbol, duplicando lógica. Pydantic v2 soporta modelos recursivos con `model_rebuild()`.

### 4. Integración con UoW

**Decisión:** registrar `CategoriaRepository` en la función de dependencia `get_uow()` del módulo de categorías, igual que hacen los módulos de auth y usuarios.

```python
def get_uow() -> Generator[UnitOfWork, None, None]:
    uow = UnitOfWork(get_session_factory())
    uow.repos.register("categorias", lambda s: CategoriaRepository(s))
    with uow:
        yield uow
```

**Rationale:** Consistente con el patrón existente. Alternativa: registro global en `main.py` — acoplamiento innecesario y viola el principio de feature-first.

### 5. Validación de productos activos antes de soft delete (RN-CA03)

**Decisión:** el service consulta `ProductoCategoria` antes del soft delete. Si hay productos con `deleted_at IS NULL`, lanza `HTTP 409`.

**Rationale:** La query es directa y el conteo es barato. No se necesita repositorio de productos completo — solo un conteo vía SQL.

## Risks / Trade-offs

- **[Riesgo] CTE de profundidad arbitraria en árbol muy profundo** → el sistema no usa categorías con más de 3-4 niveles en práctica (comida). Mitigación: sin acción en v1; documentar límite recomendado de 5 niveles.
- **[Riesgo] Subcategorías huérfanas al borrar padre** → spec RN requiere que las subcategorías deban reasignarse o eliminarse antes del soft delete del padre. El service valida esto igual que los productos activos.
- **[Trade-off] Raw SQL vs ORM puro** → raw SQL CTE es más eficiente pero menos "idiomático" para SQLAlchemy. Aceptable porque está encapsulado en el Repository, sin filtrarse hacia capas superiores.

## Migration Plan

1. No hay cambios en el modelo ni migraciones Alembic (tabla `categoria` ya existe desde `0.3`).
2. Implementar en orden: `schemas.py` (agregar `CategoriaTree`) → `repository.py` → `service.py` → `router.py` → `api/v1/router.py`.
3. Verificar con `GET /api/v1/categorias` (debe retornar `[]` en DB vacía, sin error).
