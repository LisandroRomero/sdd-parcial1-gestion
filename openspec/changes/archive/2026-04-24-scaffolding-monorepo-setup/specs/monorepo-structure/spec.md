## ADDED Requirements

### Requirement: Repository has organized monorepo structure
The repository SHALL have a clear separation between backend and frontend directories at the root level, with each containing a well-defined internal structure following architectural patterns.

#### Scenario: Backend directory exists with feature-first structure
- **WHEN** a developer clones the repository
- **THEN** a `/backend` directory exists containing subdirectories for each feature (auth, usuarios, productos, categorias, ingredientes, pedidos, pagos, direcciones, admin, refreshtokens) plus a `/core` directory for shared infrastructure

#### Scenario: Each backend feature has required files
- **WHEN** examining a feature subdirectory (e.g., /backend/auth/)
- **THEN** it contains: model.py, schemas.py, repository.py, service.py, router.py

#### Scenario: Frontend directory exists with FSD structure
- **WHEN** a developer clones the repository
- **THEN** a `/frontend` directory exists containing: app/, pages/, features/, entities/, shared/, public/

### Requirement: Backend uses feature-first vertical slice architecture
The backend SHALL organize code into vertical feature slices, each containing all layers (model, schema, repository, service, router) to maximize cohesion and minimize coupling.

#### Scenario: Each backend feature is self-contained
- **WHEN** implementing a feature endpoint (e.g., product creation)
- **THEN** all related code is co-located in the same feature directory: models, schemas, data access, business logic, and HTTP handlers

#### Scenario: Core infrastructure is separate
- **WHEN** looking for shared infrastructure (database configuration, security utilities)
- **THEN** these are in /backend/core/ and imported by features as needed

### Requirement: Frontend uses Feature-Sliced Design (FSD) architecture
The frontend SHALL organize code into layers (app, pages, features, entities, shared) following the FSD methodology to ensure clear separation of concerns and reduce dependency cycles.

#### Scenario: App layer contains root component and routing
- **WHEN** starting the frontend application
- **THEN** the app/ directory contains the root component, routing configuration, and global providers

#### Scenario: Pages are organized by route
- **WHEN** navigating to a page (e.g., /products, /cart)
- **THEN** corresponding page components exist in pages/ directory

#### Scenario: Features are self-contained modules
- **WHEN** implementing a feature (e.g., user authentication, product filtering)
- **THEN** all feature-specific components, hooks, and utilities are in features/ directory

#### Scenario: Entities contain domain models and shared state
- **WHEN** implementing shared domain logic or state management
- **THEN** entity models and Zustand stores are in entities/ directory

#### Scenario: Shared utilities are globally available
- **WHEN** needing utilities, constants, API clients, or UI components used across the app
- **THEN** these are in shared/ directory and imported from there

### Requirement: Directory structure is documented and discoverable
The repository structure SHALL be clearly documented and follow naming conventions that are self-explanatory for new developers.

#### Scenario: Root README explains structure
- **WHEN** a developer reads the root README.md
- **THEN** it explains the purpose of /backend, /frontend, and provides a folder structure overview

#### Scenario: Backend conventions are clear
- **WHEN** examining the /backend directory
- **THEN** the structure follows the documented feature-first pattern consistently across all features

#### Scenario: Frontend conventions are clear
- **WHEN** examining the /frontend directory
- **THEN** the structure follows FSD layers consistently and uses documented naming patterns
