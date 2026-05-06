## ADDED Requirements

### Requirement: Backend can start with a single FastAPI entrypoint
The backend SHALL provide a single application entrypoint that boots a FastAPI app and serves HTTP requests.

#### Scenario: Developer starts the API locally
- **WHEN** a developer runs the backend server command documented in `backend/README.md`
- **THEN** the FastAPI application starts successfully and listens on a configurable host/port

### Requirement: API is versioned under /api/v1
The backend SHALL expose its public HTTP API under a versioned prefix to allow future evolution.

#### Scenario: Client calls a versioned endpoint
- **WHEN** a client requests any implemented endpoint
- **THEN** the route is mounted under `/api/v1/...` (not at the root)

### Requirement: Configuration is centralized and environment-driven
The backend SHALL load its runtime configuration from environment variables (optionally via a `.env` file) using a single typed settings module.

#### Scenario: Missing required environment variable fails fast
- **WHEN** the backend starts and a required configuration value is missing
- **THEN** startup fails with a clear error message describing the missing setting

### Requirement: Backend provides a database engine and per-request sessions
The backend SHALL provide a PostgreSQL database engine configuration and a per-request SQLModel/SQLAlchemy session factory.

#### Scenario: Request handler can obtain a DB session
- **WHEN** a router handler requires database access
- **THEN** it can obtain a session via a shared dependency (e.g., `get_session`) and execute queries within that session

### Requirement: Unit of Work supports commit/rollback around operations
The backend SHALL provide a Unit of Work abstraction that wraps a database session and provides commit/rollback behavior.

#### Scenario: Successful operation commits
- **WHEN** a service completes a write operation without errors
- **THEN** changes are committed to the database via the Unit of Work

#### Scenario: Failed operation rolls back
- **WHEN** a service raises an exception during a write operation
- **THEN** the Unit of Work rolls back the transaction and no partial writes are persisted

### Requirement: Alembic migrations are configured for SQLModel metadata
The backend SHALL be configured with Alembic to manage schema migrations for SQLModel models.

#### Scenario: Apply migrations to database
- **WHEN** a developer runs `alembic upgrade head`
- **THEN** the database schema is upgraded to the latest revision successfully

#### Scenario: Generate a new migration revision
- **WHEN** a developer introduces a schema change and runs the migration generation command
- **THEN** a new Alembic revision file is created under `backend/alembic/versions/` (or equivalent configured path)

### Requirement: Development environment template exists for backend
The backend SHALL include a `backend/.env.example` documenting all required environment variables with safe placeholder values.

#### Scenario: Developer can bootstrap env file
- **WHEN** a developer copies `backend/.env.example` to `backend/.env`
- **THEN** the file contains documented keys for database connection, JWT secrets, CORS origins, and MercadoPago credentials placeholders
