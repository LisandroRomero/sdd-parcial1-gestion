## 1. Dependencies

- [x] 1.1 Add `pyjwt` and `passlib[bcrypt]` to `backend/requirements.txt`
- [x] 1.2 Add `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` to `backend/.env.example` and `backend/core/config.py`

## 2. Core Exceptions

- [x] 2.1 Create `backend/core/exceptions.py` with `AppException` base class carrying `status_code` and `detail`
- [x] 2.2 Add `NotFoundException` (404), `ConflictException` (409), `UnauthorizedException` (401), `ForbiddenException` (403), `ValidationException` (422)

## 3. BaseRepository

- [x] 3.1 Create `backend/core/patterns.py` with generic `BaseRepository[T]` class
- [x] 3.2 Implement `add(entity)`, `get(id)`, `get_by(**filters)`, `list(skip, limit)`, `update(entity)`, `delete(entity)`, `exists(**filters)`
- [x] 3.3 Add soft-delete awareness: auto-filter `deleted_at IS NULL` and `list(include_deleted=True)` override

## 4. Security Utilities

- [x] 4.1 Create `backend/core/security.py` with `hash_password()` and `verify_password()` using passlib bcrypt
- [x] 4.2 Implement `create_access_token(subject, data)` with configurable TTL
- [x] 4.3 Implement `create_refresh_token(subject)` with longer TTL
- [x] 4.4 Implement `verify_token(token)` that returns payload or raises `UnauthorizedException`

## 5. Unit of Work Enhancement

- [x] 5.1 Refactor `backend/core/uow.py` to expose a `repos` namespace for repository access
- [x] 5.2 Implement lazy initialization of repositories on first access via `repos` namespace
- [x] 5.3 Ensure all repos in `uow.repos` share the same session and commit atomically

## 6. Auth Dependencies (FastAPI DI)

- [x] 6.1 Create `backend/core/dependencies.py` with `get_current_user` dependency that extracts JWT from Authorization header and returns `Usuario`
- [x] 6.2 Implement `require_role(*roles)` dependency factory for RBAC (returns 403 if missing role)
- [x] 6.3 Implement `get_uow` dependency that creates a per-request UnitOfWork with commit on success / rollback on error

## 7. Middleware

- [x] 7.1 Create `backend/core/middleware.py` with exception handling middleware that maps `AppException` to HTTP status codes
- [x] 7.2 Add `X-Request-ID` middleware that generates UUID for each request and echoes client-provided IDs

## 8. API Routing & Wiring

- [x] 8.1 Update `backend/api/v1/router.py` to include feature router stubs (auth, usuarios, productos, categorias, ingredientes, pedidos, pagos, direcciones) — commented out or conditional, ready to enable when routers are implemented
- [x] 8.2 Wire middleware into `backend/main.py` `create_app()` factory: register exception handler, request ID middleware
- [x] 8.3 Wire auth dependencies into `backend/main.py`: ensure JWT settings validation on startup
