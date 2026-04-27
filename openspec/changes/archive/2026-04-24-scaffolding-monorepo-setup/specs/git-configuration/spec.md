## ADDED Requirements

### Requirement: .gitignore prevents secrets and build artifacts from being committed
The repository SHALL have a .gitignore file at the root that excludes sensitive files, environment variables, dependencies, and build artifacts.

#### Scenario: Environment files are ignored
- **WHEN** developers create local .env files with sensitive credentials
- **THEN** these files are never tracked by Git and cannot be accidentally committed

#### Scenario: Python-specific artifacts are ignored
- **WHEN** running Python locally and caching bytecode
- **THEN** __pycache__/ directories, *.pyc files, and .venv/ are not tracked

#### Scenario: Node.js artifacts are ignored
- **WHEN** installing frontend dependencies
- **THEN** node_modules/ and dist/ directories are not tracked

#### Scenario: IDE and OS files are ignored
- **WHEN** developers use different IDEs and operating systems
- **THEN** .DS_Store, .vscode/, .idea/ and similar are not tracked

#### Scenario: Developers cannot bypass .gitignore easily
- **WHEN** a developer attempts to force-add a .env file
- **THEN** it fails or triggers a pre-commit hook (implemented in follow-up changes)

### Requirement: .env.example documents required environment variables
The repository SHALL include .env.example files in backend and frontend directories that document all required environment variables with example values.

#### Scenario: Backend .env.example exists with documented variables
- **WHEN** a developer clones the repository and reads backend/.env.example
- **THEN** it lists all required variables (DATABASE_URL, SECRET_KEY, JWT_*, CORS_ORIGINS, MERCADOPAGO_*, etc.) with comments explaining their purpose

#### Scenario: Frontend .env.example exists with documented variables
- **WHEN** a developer clones the repository and reads frontend/.env.example
- **THEN** it lists required variables (VITE_API_BASE_URL, VITE_MERCADOPAGO_PUBLIC_KEY, etc.) with comments

#### Scenario: .env.example uses safe placeholder values
- **WHEN** examining .env.example files
- **THEN** they contain obviously fake or test values (e.g., TEST-xxx, localhost, development) rather than real secrets

#### Scenario: Developers can quickly set up by copying .env.example
- **WHEN** following setup instructions
- **THEN** developers can run `cp .env.example .env` and then edit values for their local environment

### Requirement: Git configuration supports team workflows
The repository SHALL be configured to support conventional commits, clear history, and collaboration best practices.

#### Scenario: Repository supports SSH and HTTPS cloning
- **WHEN** cloning the repository
- **THEN** both SSH and HTTPS URLs work correctly

#### Scenario: Default branch is main
- **WHEN** cloning the repository
- **THEN** the default branch is named 'main' (not 'master')

#### Scenario: Commits follow conventional commits format
- **WHEN** reviewing Git history
- **THEN** commit messages follow pattern: `<type>(<scope>): <subject>` (e.g., `feat(auth): add user registration endpoint`)
