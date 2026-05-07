## Context

Food Store es un e-commerce full-stack con backend FastAPI + SQLModel + PostgreSQL 16. Actualmente existe toda la infraestructura base:

- Conexión a BD configurada (`core/database.py` con `create_engine` + `get_session`)
- UnitOfWork implementado (`core/uow.py` con commit/rollback automático)
- Alembic configurado con metadata de SQLModel y migración baseline vacía (`0001_baseline.py`)
- Docker Compose con PostgreSQL 16 (puerto 5432, database `foodstore`)
- 9 módulos backend con estructura feature-first (model/schemas/repository/service/router) — **todos vacíos**
- 4 specs archivadas que cubren infraestructura base pero **ninguna cubre modelo de datos**

El proyecto necesita sus **15 tablas del ERD v5** para que cualquier módulo de negocio pueda operar. Sin modelos, no hay datos. Sin datos, no hay funcionalidad.

## Goals / Non-Goals

**Goals:**

- Definir los 15 modelos SQLModel correspondientes al ERD v5 en sus respectivos módulos
- Crear schemas Pydantic Create/Update/Read para cada entidad
- Generar migración Alembic `0002_create_all_tables.py` vía autogenerate
- Implementar script de seed con catálogos fijos (roles, estados, formas de pago) y usuario admin
- Agregar dependencias faltantes al backend (`sqlmodel`, `alembic`, `psycopg[binary]`, `passlib[bcrypt]`, `pydantic[email-validator]`)

**Non-Goals:**

- Lógica de negocio en servicios o repositorios (se implementa en changes posteriores por módulo)
- Endpoints REST o routers (idem)
- Validaciones de negocio complejas (más allá de tipos básicos Pydantic)
- Frontend de ningún tipo
- Integración con MercadoPago
- Sistema de autenticación JWT (requiere módulo auth funcional sobre estos modelos)

## Decisions

### 1. SQLModel sobre SQLAlchemy puro

**Decisión:** Usar SQLModel (que ya es dependencia del proyecto) en lugar de SQLAlchemy puro.

**Por qué:** SQLModel unifica el modelo de BD con el schema Pydantic en una sola clase, reduciendo la duplicación. El proyecto ya eligió SQLModel en la configuración de Alembic y core.

**Alternativa considerada:** SQLAlchemy ORM puro + Pydantic por separado. Descartado porque duplica definiciones de campos y rompe con la configuración existente.

### 2. Catálogos como tablas (no Enums de Python)

**Decisión:** `Rol`, `EstadoPedido` y `FormaPago` se modelan como tablas SQLModel con PK semántica (VARCHAR), NO como Enums de Python.

**Por qué:** Permite FK reales a nivel BD, consultas JOIN directas, y agregar nuevos valores sin recompilar el código. El ERD v5 las define explícitamente como tablas.

**Alternativa considerada:** Enums de Python + campo VARCHAR con check constraint. Descartado porque las FK reales son más seguras y el seed ya define los valores iniciales.

### 3. Snapshot pattern en DetallePedido

**Decisión:** `DetallePedido` almacena `nombre_snapshot` y `precio_snapshot` como copia de los valores del producto al momento del pedido.

**Por qué:** El ERD v5 lo exige. Un pedido debe reflejar los precios y nombres del momento de la compra, no los actuales (que pueden cambiar).

### 4. Soft-delete con `deleted_at` nullable

**Decisión:** Usar columna `deleted_at: datetime | None` para borrado lógico en Usuario, Categoria, Producto.

**Por qué:** El ERD v5 especifica soft-delete. Facilita recovery y auditoría. La responsabilidad de filtrar `WHERE deleted_at IS NULL` recaerá en los repositorios.

**Impacto:** Los repositorios base (`BaseRepository`) deberán aplicar este filtro automáticamente en queries de listado.

### 5. Composite primary keys para tablas N:M

**Decisión:** `UsuarioRol`, `ProductoCategoria`, `ProductoIngrediente` usan PK compuesta `(entidad_a_id, entidad_b_id)`.

**Por qué:** Modela directamente la restricción de unicidad. SQLModel soporta `CompositeKey` via `__table_args__`.

### 6. TIMESTAMPTZ con server_default = func.now()

**Decisión:** Todos los campos `created_at` usan `TIMESTAMP WITH TIME ZONE` con `server_default=func.now()`.

**Por qué:** Consistencia horaria independiente del servidor de aplicación. PostgreSQL maneja la zona horaria correctamente.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| Alembic autogenerate puede no capturar `ARRAY(INTEGER)` (personalizacion en DetallePedido) | Revisar manualmente la migración generada y corregir si es necesario |
| `sa.Enum` vs VARCHAR con check no cubierto por autogenerate | Todos los catálogos se modelan como tablas FK, evitando este problema |
| Seed corrido múltiples veces duplica datos | Usar `IF NOT EXISTS` o upsert en el script de seed |
| Soft-delete olvidado en queries futuras | El `BaseRepository` aplicará `deleted_at IS NULL` automáticamente |
| 15 modelos en un solo change puede ser mucha coordinación | Los modelos se distribuyen por módulo, cada uno autocontenido; se implementan en orden (usuarios → catálogo → pedidos/pagos) |
