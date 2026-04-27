## Context

Food Store is a monorepo e-commerce platform for food delivery. The project will use Python/FastAPI for the backend and React/TypeScript/Vite for the frontend. Both need to be scaffolded with clear folder structures that support feature-first (backend) and Feature-Sliced Design (frontend) architectures. The repository must be secure (sensitive files excluded) and well-documented from day one.

## Goals / Non-Goals

**Goals:**
- Establish a production-ready folder structure for both backend and frontend
- Define clear naming conventions and module patterns
- Ensure `.env` and sensitive files are never committed
- Provide clear onboarding documentation (README, .env.example)
- Set up commit history to show incremental progress (not squashing into one commit)

**Non-Goals:**
- Setting up CI/CD pipelines (that's a separate change)
- Installing all dependencies (comes in follow-up changes for backend/frontend setup)
- Configuring databases or external services
- Writing any application code (this is just scaffolding)

## Decisions

### 1. Monorepo Structure (vs. Polyrepo)
**Decision**: Single Git repository with `/backend` and `/frontend` directories.

**Rationale**: 
- Monorepos simplify dependency management between layers
- Easier to coordinate changes across backend and frontend
- Single CI/CD pipeline and shared tooling

**Alternatives considered**:
- Polyrepo: More independent scaling but harder to coordinate breaking changes
- Workspaces (Lerna, Turbo): Possible future optimization; simple monorepo is sufficient now

### 2. Backend Structure: Feature-First Vertical Slices
**Decision**: Each feature gets its own directory with model, schema, repository, service, and router.

Structure:
```
backend/
├── auth/
│   ├── model.py       (SQLModel entities)
│   ├── schemas.py     (Pydantic request/response)
│   ├── repository.py  (DB queries)
│   ├── service.py     (business logic)
│   └── router.py      (FastAPI endpoints)
├── usuarios/
├── productos/
├── ...
└── core/              (shared: config, security, database)
```

**Rationale**: 
- Vertical slices promote cohesion and reduce cross-module dependencies
- Easy to find related code: all auth logic in one place
- Scales well as the codebase grows

**Alternatives considered**:
- Horizontal layers (models/, services/, routers/): Leads to scattered logic
- Domain-driven design: Good but more complex for this scale

### 3. Frontend Structure: Feature-Sliced Design (FSD)
**Decision**: Layered architecture with `app/`, `pages/`, `features/`, `entities/`, `shared/`.

Structure:
```
frontend/
├── app/          (root app component, routing)
├── pages/        (page-level components)
├── features/     (feature-specific logic)
├── entities/     (domain models, stores)
├── shared/       (utilities, constants, API client)
└── public/       (static assets)
```

**Rationale**:
- FSD is battle-tested for React apps with clear separation
- Reduces dependency hell and circular imports
- Encourages atomic design patterns

**Alternatives considered**:
- Flat structure: Works for small projects but becomes chaotic
- Module-per-feature: Similar but less standardized

### 4. Environment Configuration
**Decision**: 
- `.env` file is git-ignored (local configuration only)
- `.env.example` is committed with all variables and example values
- Both backend and frontend have their own `.env.example`

**Rationale**:
- Prevents accidental commits of API keys, DB credentials
- `.env.example` documents required variables for developers
- Two examples (backend/frontend) keep concerns separate

### 5. Root-Level Documentation
**Decision**: 
- `README.md` at repository root with setup instructions
- Links to backend and frontend READMEs for specific details

**Rationale**:
- Developers can onboard quickly
- Single entry point for understanding the project structure
- Clear instructions for clone, install, and run

### 6. Commit Strategy
**Decision**: Progressive commits for each folder/file created (not a single squashed commit).

**Rationale**:
- Shows structure evolution clearly in git history
- Easier to revert partial changes if needed
- Follows conventional commits pattern

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Developers accidentally commit `.env` | Use git hooks (husky) in a follow-up change to enforce `.gitignore` |
| Folder structure becomes inconsistent | Document conventions in README; code review checklist |
| Backend/frontend get out of sync | CI/CD pipeline validates both in follow-up changes |
| .env.example becomes stale | Include reminder in README to keep it in sync |

## Open Questions

- Should we use `poetry` or `pip` for Python dependencies? (Decided later in backend setup)
- Should we use `npm`, `yarn`, or `pnpm` for frontend? (Decided later in frontend setup)
- Do we need a `/docs` directory for architecture/ADRs? (Can add in a future change)
