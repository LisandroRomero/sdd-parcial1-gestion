## Context

El backend de Food Store está en una etapa temprana: los modelos SQLModel y schemas Pydantic están completos (8 módulos), pero toda la capa de infraestructura base está ausente. No existe un `BaseRepository` genérico, no hay manejo centralizado de excepciones, no hay utilities de seguridad JWT, no hay dependencias de autenticación/authorización para FastAPI, ni middleware global. El `UnitOfWork` existente es funcional pero minimalista — no conoce repositorios.

Esto significa que cualquier intento de implementar repositories, services y routers tendría que hacerlo desde cero, sin consistencia entre módulos y duplicando lógica.

## Goals / Non-Goals

**Goals:**
- Proveer un `BaseRepository[T]` genérico con operaciones CRUD base, paginación, y soporte de soft-delete
- Definir una jerarquía de excepciones personalizadas que se mapeen automáticamente a códigos HTTP
- Implementar utilities de JWT (creación y verificación de access/refresh tokens) y password hashing
- Crear dependencias FastDI para `get_current_user` y `require_role`
- Agregar middleware global de error handling y request ID
- Integrar repositorios en el Unit of Work (`uow.repos.{nombre}`)
- Dejar la estructura base de routing preparada en `api/v1/router.py`

**Non-Goals:**
- NO implementar repositories específicos de dominio (eso se hará por módulo en cambios posteriores)
- NO implementar services ni routers de dominio
- NO implementar la lógica de negocio de autenticación (login, registro) — solo las utilities
- NO agregar tests (se cubrirá en cambio dedicado)
- NO modificar modelos, schemas, migraciones, ni seed existentes

## Decisions

### 1. BaseRepository sincrónico (no async)
- **Decisión**: `BaseRepository[T]` usará `Session` sincrónica de SQLAlchemy, igual que el UoW existente.
- **Motivo**: El proyecto ya usa SQLAlchemy sincrónico en toda la base. Migrar a async ahora agregaría complejidad sin beneficio inmediato. Se puede migrar después si es necesario.
- **Alternativa**: async session → implicaría cambiar `database.py`, `uow.py`, y toda la base existente. Fuera de scope.

### 2. Exception hierarchy con HTTPException mapping automático
- **Decisión**: Cada excepción personaliza tendrá un `status_code` y `detail` que se mapea automáticamente a `HTTPException` via un middleware handler.
- **Motivo**: Los services pueden lanzar `NotFoundException` sin importar FastAPI, y el middleware se encarga de convertirlo. Esto mantiene la capa de negocio limpia de dependencias HTTP.
- **Alternativa**: Lanzar `HTTPException` directamente desde services → acopla lógica de negocio a FastAPI. Descartado.

### 3. passlib con bcrypt para password hashing
- **Decisión**: Usar `passlib.context.CryptContext` con esquema `bcrypt` (cost factor 12).
- **Motivo**: passlib provee una abstracción que permite rotar esquemas de hashing en el futuro sin cambiar código cliente. bcrypt rounds=12 es el estándar de la industria.
- **Alternativa**: bcrypt directo → menos flexible para migración futura de esquemas.

### 4. PyJWT para tokens
- **Decisión**: Usar `PyJWT` para crear y verificar tokens JWT.
- **Motivo**: Biblioteca estándar, madura, bien mantenida. El proyecto no necesita la capa de ORM de `python-jose`.
- **Alternativa**: `python-jose` → integración con ORM, pero más peso y menos usado.

### 5. Repositorios registrados como atributos tipados del UoW
- **Decisión**: Cada módulo registrará su repositorio como un atributo de `UnitOfWork` (ej. `uow.repos.producto`), usando `@property` o inyección en `__init__`.
- **Motivo**: Acceso natural y type-safe: `uow.repos.producto.add(...)`. El UoW conoce todos los repositorios y asegura que compartan la misma sesión.
- **Alternativa**: Repositorios independientes que reciben session → sin garantía de misma transacción entre repos.

### 6. Middleware como lista en FastAPI add_middleware
- **Decisión**: Usar `app.add_middleware()` de FastAPI (Starlette middleware) en lugar de dependencias o decoradores.
- **Motivo**: Los middleware de Starlette se ejecutan en el ciclo de request/response completo y son el mecanismo estándar.
- **Alternativa**: Dependencias FastAPI → solo cubren path operations, no request/response global.

## Risks / Trade-offs

- **[Riesgo] BaseRepository genérico puede ser demasiado rígido para casos específicos** → Mitigación: los métodos son `virtual` (overrideables) y se puede acceder a `self.session` directamente en subclases si necesitan queries custom.
- **[Trade-off] Sincrónico ahora facilita el desarrollo pero limita throughput** → Aceptable para las cargas iniciales del proyecto. Migrar a async en el futuro requiere cambiar `database.py` y `uow.py` pero no afecta repositories individuales si se abstrae bien.
- **[Riesgo] passlib con bcrypt puede ser lento en tests** → Mitigación: usar rounds=4 en entorno de test via configuración.
- **[Riesgo] Repositorios registrados en UoW crean acoplamiento** → Mitigación: el UoW solo conoce la interfaz `BaseRepository[T]`, no implementaciones concretas. Cada repo es independiente.
