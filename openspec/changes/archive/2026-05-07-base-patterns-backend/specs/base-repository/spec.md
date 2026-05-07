## ADDED Requirements

### Requirement: BaseRepository[T] provides generic CRUD operations
The system SHALL provide a generic `BaseRepository[T]` abstract class that implements standard CRUD operations for any SQLModel entity.

#### Scenario: Repository can add a new entity
- **WHEN** `repo.add(entity)` is called with a valid SQLModel instance
- **THEN** the entity is added to the session (pending commit via UoW)

#### Scenario: Repository can retrieve an entity by ID
- **WHEN** `repo.get(id)` is called with a valid primary key value
- **THEN** the corresponding entity is returned, or `None` if not found

#### Scenario: Repository can retrieve a single entity by arbitrary filter
- **WHEN** `repo.get_by(**filters)` is called with column-value pairs
- **THEN** the first matching entity is returned, or `None` if no match

#### Scenario: Repository can list entities with pagination
- **WHEN** `repo.list(skip=0, limit=100)` is called with pagination parameters
- **THEN** a list of entities is returned, respecting the skip/limit bounds

#### Scenario: Repository can update an entity
- **WHEN** `repo.update(entity)` is called with a modified SQLModel instance
- **THEN** the changes are merged into the session (pending commit via UoW)

#### Scenario: Repository can hard-delete an entity
- **WHEN** `repo.delete(entity)` is called with an existing entity
- **THEN** the entity is marked for deletion in the session

#### Scenario: Repository can check entity existence
- **WHEN** `repo.exists(**filters)` is called with column-value pairs
- **THEN** returns `True` if at least one matching entity exists, `False` otherwise

### Requirement: BaseRepository[T] supports soft-delete awareness
The system SHALL allow repositories to be soft-delete aware, automatically filtering out soft-deleted records from standard queries.

#### Scenario: Soft-delete repository excludes deleted records
- **WHEN** a soft-delete-aware repository performs `list()` or `get()`
- **THEN** records with a non-null `deleted_at` are excluded by default

#### Scenario: Soft-delete repository can override default filter
- **WHEN** `list(include_deleted=True)` is called
- **THEN** all records including soft-deleted ones are returned

#### Scenario: Soft-delete sets deleted_at timestamp
- **WHEN** `repo.delete(entity)` is called on a soft-delete-aware repository
- **THEN** the entity's `deleted_at` is set to the current timestamp instead of removing the row
