# Food Store — E-Commerce Platform

A modern, feature-rich e-commerce platform for food delivery built with Python (FastAPI) backend and React (TypeScript) frontend.

## 📁 Project Structure

This is a **monorepo** containing both backend and frontend components:

```
food-store/
├── backend/                 # Python/FastAPI backend (feature-first architecture)
│   ├── auth/               # Authentication module
│   ├── usuarios/           # User management
│   ├── productos/          # Product catalog
│   ├── categorias/         # Product categories
│   ├── ingredientes/       # Ingredients & allergens
│   ├── pedidos/            # Order management
│   ├── pagos/              # Payment processing (MercadoPago)
│   ├── direcciones/        # Delivery addresses
│   ├── admin/              # Admin functions
│   ├── refreshtokens/      # Token management
│   ├── core/               # Shared infrastructure
│   └── README.md           # Backend-specific documentation
│
├── frontend/               # React/TypeScript frontend (FSD architecture)
│   ├── app/                # Root application component
│   ├── pages/              # Page-level components
│   ├── features/           # Feature-specific business logic
│   ├── entities/           # Domain models and stores
│   ├── shared/             # Shared utilities and components
│   ├── public/             # Static assets
│   └── README.md           # Frontend-specific documentation
│
├── .gitignore              # Git ignore rules
├── .env.example            # Example environment variables
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.10+, PostgreSQL 13+
- **Frontend**: Node.js 18+, npm/yarn/pnpm

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/food-store.git
cd food-store
```

### 2. Backend Setup

See [backend/README.md](./backend/README.md) for detailed instructions.

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
pip install -r requirements.txt  # or: poetry install
alembic upgrade head
python -m scripts.seed
uvicorn main:app --reload
```

Backend runs on: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### 3. Frontend Setup

See [frontend/README.md](./frontend/README.md) for detailed instructions.

```bash
cd frontend
cp .env.example .env
# Edit .env with your configuration
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

## 🏗️ Architecture

### Backend: Feature-First Vertical Slices

Each feature (auth, productos, pedidos, etc.) is a self-contained vertical slice:

```
backend/auth/
├── model.py          # SQLModel entity definitions
├── schemas.py        # Pydantic request/response models
├── repository.py     # Database queries
├── service.py        # Business logic
└── router.py         # FastAPI endpoints
```

**Core Infrastructure** (`backend/core/`):
- Database configuration
- Security utilities (JWT, password hashing)
- Shared dependencies
- Exception handling

### Frontend: Feature-Sliced Design (FSD)

Organized in layers from low-level to high-level:

1. **shared/**: Reusable utilities, components, constants
2. **entities/**: Domain models, Zustand stores
3. **features/**: Feature-specific business logic and UI
4. **pages/**: Page-level components
5. **app/**: Root component, routing, global providers

## 📋 Development Workflow

### Creating a New Feature

1. **Backend**: Create a new directory under `backend/` with the 5-file pattern (model, schemas, repository, service, router)
2. **Frontend**: Create feature directory under `frontend/features/` with components, hooks, stores as needed
3. **Commit**: Use conventional commits: `feat(auth): add login endpoint`

### Conventional Commits

Format: `<type>(<scope>): <subject>`

Examples:
- `feat(auth): add user registration`
- `fix(productos): correct stock calculation`
- `docs: update README with setup instructions`
- `refactor(pedidos): simplify state machine logic`

### Git Workflow

1. Create a feature branch: `git checkout -b feat/user-auth`
2. Make changes and commit progressively (not one massive commit)
3. Create a Pull Request with clear description
4. Code review and merge to main

## 🔐 Security Notes

- **Never commit** `.env` files with real secrets
- Use `.env.example` as template for environment variables
- MercadoPago tokens are in `.env` (never hardcoded)
- Database credentials are environment-based
- JWT secrets are environment-based (never hardcoded)

## 📚 Additional Documentation

- [Backend Documentation](./backend/README.md) — FastAPI setup, database, API conventions
- [Frontend Documentation](./frontend/README.md) — React setup, FSD structure, state management

## 🤝 Contributing

1. Follow the project structure and naming conventions
2. Use conventional commits
3. Ensure code passes linting and tests (to be implemented)
4. Create clear Pull Requests with description of changes

## 📝 License

[Specify your license here]
