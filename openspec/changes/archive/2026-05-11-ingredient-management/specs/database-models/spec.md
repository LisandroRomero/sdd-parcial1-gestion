## MODIFIED Requirements

### Requirement: Modelo Ingrediente
El sistema SHALL definir el modelo `Ingrediente` en `backend/ingredientes/model.py` con los campos: `nombre VARCHAR(100) UNIQUE NOT NULL`, `es_alergeno BOOLEAN NOT NULL DEFAULT false`, `created_at TIMESTAMPTZ DEFAULT now()`, y `deleted_at TIMESTAMPTZ NULL` para soft delete. El campo `deleted_at` es nuevo respecto al modelo actual y requiere migración Alembic.

#### Scenario: Ingrediente tiene nombre único
- **WHEN** se define Ingrediente
- **THEN** SHALL tener constraint `UNIQUE` sobre `nombre`

#### Scenario: Ingrediente tiene soft delete
- **WHEN** se define Ingrediente
- **THEN** SHALL tener campo `deleted_at TIMESTAMPTZ NULL`

#### Scenario: Migración agrega columna deleted_at
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** la tabla `ingrediente` tiene la columna `deleted_at TIMESTAMPTZ NULL` sin romper filas existentes
