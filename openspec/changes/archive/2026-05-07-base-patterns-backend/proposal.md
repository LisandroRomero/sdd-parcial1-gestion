## Why

El backend de Food Store tiene los modelos SQLModel y schemas Pydantic definidos, pero carece de toda la infraestructura base necesaria para implementar las capas de negocio. No existe `BaseRepository`, no hay utilities de seguridad (JWT, hashing), no hay DI de autenticación, no hay excepciones personalizadas, y el Unit of Work no está integrado con repositorios. Sin esta base, cada módulo tendría que implementar CRUD desde cero y no habría consistencia entre módulos.

## What Changes

- **Crear `core/patterns.py`** con `BaseRepository[T]` genérico con operaciones CRUD base (`add`, `get`, `list`, `update`, `delete`, `exists`)
- **Crear `core/exceptions.py`** con excepciones personalizadas (`NotFoundException`, `ConflictException`, `UnauthorizedException`, `ForbiddenException`, `ValidationException`)
- **Crear `core/security.py`** con utilities de JWT (create/verify access & refresh tokens) y password hashing con bcrypt
- **Crear `core/dependencies.py`** con dependencias FastAPI: `get_current_user`, `require_role`, `get_uow`
- **Crear `core/middleware.py`** con middleware de error handling y request ID
- **Mejorar `core/uow.py`** para integrar repositorios (que `uow.repos.{repositorio}` funcione)
- **Actualizar routers base** en `api/v1/router.py` para incluir estructura de features (aunque los routers individuales se implementen después)

## Capabilities

### New Capabilities
- `base-repository`: Generic `BaseRepository[T]` with full CRUD, pagination, soft-delete awareness, and type-safe operations
- `core-exceptions`: Custom exception hierarchy for HTTP error mapping
- `jwt-auth`: JWT token creation, verification, and refresh token utilities
- `auth-dependencies`: FastAPI dependency injection for authentication (`get_current_user`) and authorization (`require_role`)
- `core-middleware`: Global middleware for error handling and request tracking
- `uow-repository`: Unit of Work pattern with integrated repository access

### Modified Capabilities
- `backend-infrastructure`: Los requirements se actualizan para incluir `BaseRepository`, `exceptions`, `security`, `dependencies`, y `middleware` como parte de la infraestructura core

## Impact

- **Backend core**: Se agregan 5 archivos nuevos y se modifica 1 existente (`uow.py`)
- **API routing**: `api/v1/router.py` se actualiza con la estructura de features
- **Dependencias**: Se requiere agregar `pyjwt`, `bcrypt` (o usar passlib con bcrypt) al `pyproject.toml`
- **No breaking**: Todo es aditivo — no se modifican modelos, schemas, ni migraciones existentes
- **Pre-requisito**: Este cambio es base necesaria para implementar todos los repositories, services y routers de los módulos de dominio
