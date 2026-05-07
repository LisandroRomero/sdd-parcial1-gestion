## ADDED Requirements

### Requirement: UnitOfWork provides access to repositories via repos namespace
The system SHALL extend the existing `UnitOfWork` to expose repositories as attributes under a `repos` namespace, sharing the same session.

#### Scenario: UoW exposes repository as attribute
- **WHEN** a service accesses `uow.repos.usuarios`
- **THEN** it receives a repository instance that uses the UoW's active session

#### Scenario: All repos in UoW share the same session
- **WHEN** a service accesses multiple repositories via `uow.repos`
- **THEN** all repositories use the same database session managed by the UoW

### Requirement: Repositories are lazily initialized within the UoW
Repositories SHALL be created on first access within a UoW context, not at UoW creation time.

#### Scenario: Repository is created on first access
- **WHEN** `uow.repos.usuarios` is accessed for the first time
- **THEN** a new `UsuarioRepository` instance is created with the UoW's session and cached for the lifetime of the UoW

### Requirement: UoW commit triggers session commit
The system SHALL ensure that `uow.commit()` commits all pending changes across all repositories to the database.

#### Scenario: Changes from multiple repos committed atomically
- **WHEN** operations are performed via two different repos (e.g., `uow.repos.usuarios.add(u1)` and `uow.repos.productos.add(p1)`) and `uow.commit()` is called
- **THEN** both changes are committed in a single database transaction
