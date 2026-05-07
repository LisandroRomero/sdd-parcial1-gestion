## ADDED Requirements

### Requirement: System provides get_current_user dependency
The system SHALL provide a FastAPI dependency that extracts and validates the current authenticated user from the JWT token in the Authorization header.

#### Scenario: Valid token returns user
- **WHEN** a request includes a valid `Authorization: Bearer <token>` header
- **THEN** `get_current_user` returns the authenticated `Usuario` from the database

#### Scenario: Missing token returns 401
- **WHEN** a request has no Authorization header
- **THEN** `get_current_user` raises an HTTP 401 Unauthorized response

#### Scenario: Invalid token returns 401
- **WHEN** a request includes a malformed or invalid token
- **THEN** `get_current_user` raises an HTTP 401 Unauthorized response

### Requirement: System provides require_role dependency
The system SHALL provide a FastAPI dependency factory that restricts access to users with specific roles.

#### Scenario: User with required role is allowed
- **WHEN** a route uses `require_role("admin")` and the authenticated user has the admin role
- **THEN** the request proceeds to the route handler

#### Scenario: User without required role gets 403
- **WHEN** a route uses `require_role("admin")` and the authenticated user does not have the admin role
- **THEN** an HTTP 403 Forbidden response is returned

#### Scenario: Multiple roles allowed
- **WHEN** a route uses `require_role("admin", "gestor_pedidos")` and the user has any of those roles
- **THEN** the request proceeds to the route handler

### Requirement: System provides get_uow dependency
The system SHALL provide a FastAPI dependency that creates a per-request Unit of Work with an active database session.

#### Scenario: Request acquires UoW with session
- **WHEN** a route handler declares `uow: UnitOfWork = Depends(get_uow)`
- **THEN** the dependency provides a ready-to-use UnitOfWork with an open session

#### Scenario: UoW commits on success
- **WHEN** the route handler completes without error
- **THEN** the UoW calls `commit()` before closing the session

#### Scenario: UoW rolls back on error
- **WHEN** the route handler raises an exception
- **THEN** the UoW calls `rollback()` and the session is closed
