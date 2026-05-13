## MODIFIED Requirements

### Requirement: UnitOfWork provides access to repositories via repos namespace
The system SHALL extend the existing `UnitOfWork` to expose repositories as attributes under a `repos` namespace, sharing the same session. The `_register_repos()` function in `core/dependencies.py` SHALL register all domain repositories, including `pedidos`, `detalles_pedido`, `productos`, and `direcciones`, in addition to `usuarios`, `usuario_roles`, and `refresh_tokens`.

#### Scenario: UoW exposes repository as attribute
- **WHEN** a service accesses `uow.repos.usuarios`
- **THEN** it receives a repository instance that uses the UoW's active session

#### Scenario: All repos in UoW share the same session
- **WHEN** a service accesses multiple repositories via `uow.repos`
- **THEN** all repositories use the same database session managed by the UoW

#### Scenario: Order creation repos are accessible via UoW
- **WHEN** the pedidos service accesses `uow.repos.pedidos`, `uow.repos.detalles_pedido`, `uow.repos.productos`, or `uow.repos.direcciones`
- **THEN** each returns the corresponding repository instance sharing the same session
