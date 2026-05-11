## Context

El módulo `backend/ingredientes/` tiene el modelo `Ingrediente` y schemas Pydantic definidos, pero `repository.py`, `service.py` y `router.py` están vacíos. El modelo carece del campo `deleted_at` que el resto del sistema usa para soft delete. La tabla ya existe en BD (creada por la migración del change `0.1`). El patrón de integración con UoW es idéntico al de `categorias`.

## Goals / Non-Goals

**Goals:**
- Agregar `deleted_at` al modelo `Ingrediente` + migración Alembic.
- Implementar `IngredienteRepository` con filtro `es_alergeno` y paginación.
- Implementar `IngredienteService` con validación de unicidad y soft delete.
- Implementar `IngredienteRouter` con endpoints `GET/POST/PUT/DELETE /api/v1/ingredientes`.
- Registrar el repositorio en UoW y el router en `api/v1/router.py`.

**Non-Goals:**
- Endpoints de asociación producto-ingrediente (`/productos/{id}/ingredientes`) — change 2.3.
- Frontend / panel admin.
- Bulk import de ingredientes.

## Decisions

### 1. Agregar `deleted_at` al modelo `Ingrediente`

**Decisión:** agregar `Optional[datetime] deleted_at = None` al modelo y generar migración Alembic con `ALTER TABLE ingrediente ADD COLUMN deleted_at TIMESTAMPTZ NULL`.

**Rationale:** la spec SDD v5 dice explícitamente "Soft delete: todos los GET filtran WHERE deleted_at IS NULL". El modelo actual no tiene el campo. Sin esta columna no se puede aplicar soft delete. La migración es non-breaking: columna nullable, sin default.

### 2. Repository simple — sin CTE, filtro por `es_alergeno`

**Decisión:** `IngredienteRepository` usa `select()` ORM estándar de SQLModel. No requiere CTE porque no hay jerarquía.

```python
def list_active(
    self, *, es_alergeno: Optional[bool], skip: int, limit: int
) -> tuple[list[Ingrediente], int]:
    stmt = select(Ingrediente).where(Ingrediente.deleted_at.is_(None))
    if es_alergeno is not None:
        stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)
    total = len(self.session.exec(stmt).all())
    items = self.session.exec(stmt.offset(skip).limit(limit)).all()
    return list(items), total
```

**Rationale:** ORM es suficiente — queries simples con filtros opcionales. No hay joins complejos ni recursión.

### 3. Validación de unicidad en el Service

**Decisión:** el service consulta `IngredienteRepository.exists_by_nombre()` antes de `create()` y `update()`. Si el nombre ya existe lanza `HTTP 409`.

**Rationale:** aunque la BD tiene `UNIQUE` sobre `nombre`, depender solo del constraint retorna un error 500 genérico de IntegrityError. El service debe atrapar esto y dar feedback claro al cliente.

### 4. Soft delete sin cascada

**Decisión:** el service aplica `ingrediente.deleted_at = now()` directamente. No valida ni modifica `ProductoIngrediente`.

**Rationale:** los ingredientes eliminados lógicamente mantienen sus asociaciones históricas con productos. El enunciado (US-014) dice "se mantiene en productos existentes". Las queries de productos deben filtrar ingredientes activos — eso es responsabilidad del módulo de productos (change 2.3).

### 5. Integración con UoW

**Decisión:** mismo patrón que `categorias` — `get_uow()` local registra `IngredienteRepository`:

```python
def get_uow() -> Generator[UnitOfWork, None, None]:
    uow = UnitOfWork(get_session_factory())
    uow.repos.register("ingredientes", lambda s: IngredienteRepository(s))
    with uow:
        yield uow
```

**Rationale:** consistente con el patrón existente, mantiene feature-first sin acoplamiento global.

### 6. Roles: ADMIN y STOCK para escritura

**Decisión:** `POST`, `PUT`, `DELETE` requieren `roles: [ADMIN, STOCK]`. `GET` es público.

**Rationale:** el enunciado indica que el Gestor de Stock puede "gestionar los ingredientes" (Descripcion.txt, línea 13). La spec Integrador.txt dice STOCK puede "ver ingredientes" — pero las user stories (US-011 a US-014) asignan el CRUD explícitamente al Gestor de Stock.

## Risks / Trade-offs

- **[Riesgo] Migración en BD con datos existentes** → `deleted_at` es `NULL` por defecto, sin impacto en filas existentes. Sin riesgo.
- **[Trade-off] Validación de unicidad O(n) vs constraint único** → la check previa es una query extra. Aceptable dado el volumen esperado (< 500 ingredientes).
- **[Riesgo] Ingredientes eliminados en personalizacion de pedidos** → las IDs de ingredientes eliminados pueden quedar en `DetallePedido.personalizacion`. No es un riesgo para este change; se trata en el módulo de pedidos.

## Migration Plan

1. Agregar `deleted_at` al modelo `Ingrediente` en `model.py`.
2. Generar migración: `alembic revision --autogenerate -m "add_deleted_at_to_ingrediente"`.
3. Verificar la migración generada (solo debe contener `ADD COLUMN deleted_at`).
4. Implementar en orden: `repository.py` → `service.py` → `router.py`.
5. Registrar en `api/v1/router.py`.
6. Verificar con `GET /api/v1/ingredientes` (debe retornar lista vacía sin error).
