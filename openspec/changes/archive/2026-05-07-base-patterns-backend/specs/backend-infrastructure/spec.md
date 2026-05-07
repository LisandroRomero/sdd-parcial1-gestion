## MODIFIED Requirements

### Requirement: Unit of Work supports commit/rollback around operations
The backend SHALL provide a Unit of Work abstraction that wraps a database session and provides commit/rollback behavior. The Unit of Work SHALL also provide access to domain repositories via a `repos` namespace.

#### Scenario: Successful operation commits
- **WHEN** a service completes a write operation without errors
- **THEN** changes are committed to the database via the Unit of Work

#### Scenario: Failed operation rolls back
- **WHEN** a service raises an exception during a write operation
- **THEN** the Unit of Work rolls back the transaction and no partial writes are persisted

#### Scenario: Repository access via UoW repos namespace
- **WHEN** a service accesses `uow.repos.usuarios`
- **THEN** it receives a repository instance that shares the UoW's active session

### Requirement: Configuration includes JWT and password hashing settings
The backend SHALL expose configuration values for JWT secret key, token expiration, and password hashing algorithm selection.

#### Scenario: JWT settings are configurable via environment
- **WHEN** the backend starts
- **THEN** JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, and REFRESH_TOKEN_EXPIRE_DAYS are loaded from environment variables with safe defaults
