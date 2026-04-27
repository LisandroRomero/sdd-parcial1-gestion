## 1. Backend Structure Setup

- [x] 1.1 Create /backend directory at repository root
- [x] 1.2 Create /backend/core directory for shared infrastructure
- [x] 1.3 Create /backend/auth directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.4 Create /backend/usuarios directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.5 Create /backend/productos directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.6 Create /backend/categorias directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.7 Create /backend/ingredientes directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.8 Create /backend/pedidos directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.9 Create /backend/pagos directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.10 Create /backend/direcciones directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.11 Create /backend/admin directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.12 Create /backend/refreshtokens directory with empty model.py, schemas.py, repository.py, service.py, router.py
- [x] 1.13 Create /backend/core/__init__.py placeholder file

## 2. Frontend Structure Setup

- [x] 2.1 Create /frontend directory at repository root
- [x] 2.2 Create /frontend/app directory
- [x] 2.3 Create /frontend/pages directory
- [x] 2.4 Create /frontend/features directory
- [x] 2.5 Create /frontend/entities directory
- [x] 2.6 Create /frontend/shared directory
- [x] 2.7 Create /frontend/public directory
- [x] 2.8 Create placeholder index.html in /frontend/public

## 3. Git Configuration

- [x] 3.1 Create root-level .gitignore file with entries for:
  - `.env` (all environment files)
  - `__pycache__/`, `*.pyc`, `.venv/` (Python)
  - `node_modules/`, `dist/` (Node.js)
  - `.DS_Store` (macOS)
  - `.vscode/`, `.idea/` (IDE files)
  - `*.log` (log files)
- [x] 3.2 Create backend/.env.example with documented variables:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
  - `JWT_REFRESH_TOKEN_EXPIRE_DAYS`
  - `CORS_ORIGINS`
  - `MERCADOPAGO_ACCESS_TOKEN`
  - `MERCADOPAGO_PUBLIC_KEY`
- [x] 3.3 Create frontend/.env.example with documented variables:
  - `VITE_API_BASE_URL`
  - `VITE_MERCADOPAGO_PUBLIC_KEY`

## 4. Documentation

- [x] 4.1 Create root-level README.md explaining:
  - Project purpose (Food Store e-commerce platform)
  - Monorepo structure (/backend, /frontend)
  - Quick start instructions
  - Links to backend/README.md and frontend/README.md
- [x] 4.2 Create backend/README.md explaining:
  - Feature-first vertical slice architecture
  - Directory structure and module organization
  - Required tools (Python version, poetry/pip)
  - Setup instructions (install dependencies, run migrations)
  - How to run the backend server
- [x] 4.3 Create frontend/README.md explaining:
  - Feature-Sliced Design (FSD) architecture
  - Layer structure (app, pages, features, entities, shared)
  - Required tools (Node.js version, npm/yarn/pnpm)
  - Setup instructions (npm install, npm run dev)
  - Dev server port (5173)

## 5. Git History Setup

- [x] 5.1 Initialize Git repository (if not already initialized)
- [x] 5.2 Add all structure and configuration files with progressive commits following conventional commits format
- [x] 5.3 Verify git log shows multiple commits (not a single squashed commit) with clear messages like:
  - `feat: initialize monorepo structure`
  - `feat(backend): scaffold feature-first directory structure`
  - `feat(frontend): scaffold FSD directory structure`
  - `docs: add root README and setup documentation`
  - `build: add .gitignore and .env examples`

## 6. Verification

- [x] 6.1 Verify /backend contains all 10 feature directories plus /core
- [x] 6.2 Verify each backend feature has all 5 required files (model.py, schemas.py, repository.py, service.py, router.py)
- [x] 6.3 Verify /frontend contains app/, pages/, features/, entities/, shared/, public/ directories
- [x] 6.4 Verify .gitignore exists at root and contains all required exclusions
- [x] 6.5 Verify backend/.env.example exists with all required variables documented
- [x] 6.6 Verify frontend/.env.example exists with all required variables documented
- [x] 6.7 Verify README.md exists at root with clear setup instructions
- [x] 6.8 Verify backend/README.md exists with backend-specific documentation
- [x] 6.9 Verify frontend/README.md exists with frontend-specific documentation
- [x] 6.10 Verify git log shows progressive commits (at least 5+ commits) with clear messages
