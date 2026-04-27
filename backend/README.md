# Backend — Food Store API (FastAPI)

Python FastAPI-based backend for the Food Store e-commerce platform using a **feature-first vertical slice architecture**.

## 🏗️ Architecture: Feature-First Vertical Slices

Each feature encapsulates all layers needed to deliver a capability:

```
backend/
├── auth/                       # Authentication & Authorization
│   ├── model.py               # User, Role, RefreshToken models
│   ├── schemas.py             # Pydantic schemas for requests/responses
│   ├── repository.py          # Database queries (users, tokens)
│   ├── service.py             # Business logic (login, register, refresh)
│   └── router.py              # FastAPI endpoints
│
├── usuarios/                   # User Management
├── productos/                  # Product Catalog
├── categorias/                 # Category Management
├── ingredientes/               # Ingredients & Allergens
├── pedidos/                    # Order Management
├── pagos/                      # Payment Processing
├── direcciones/                # Delivery Addresses
├── admin/                      # Admin Functions
├── refreshtokens/              # Token Management
│
└── core/                       # Shared Infrastructure
    ├── config.py              # Environment configuration
    ├── database.py            # SQLAlchemy session factory
    ├── security.py            # JWT, password hashing utilities
    ├── dependencies.py        # FastAPI dependency injection (get_current_user, require_role)
    ├── exceptions.py          # Custom exception classes
    └── middleware.py          # Global middleware (rate limiting, error handling)
```

**Benefits:**
- 🎯 Each feature is cohesive and self-contained
- 🔍 Easy to find related code: all auth logic in one place
- 🚀 Scales well as the codebase grows
- 🤝 Teams can work on different features in parallel without conflicts

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: 13 or higher
- **Poetry** (recommended) or pip + venv

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your editor
```

**Key variables to set:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Strong random string for JWT signing
- `CORS_ORIGINS`: Frontend URLs (e.g., http://localhost:5173)
- `MERCADOPAGO_ACCESS_TOKEN`: MercadoPago API token

### 2. Virtual Environment

```bash
# Using Poetry (recommended)
poetry install

# Or using pip + venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed initial data (roles, order states, admin user)
python -m scripts.seed
```

### 4. Start the Server

```bash
# Using Poetry
poetry run uvicorn main:app --reload

# Or using pip + venv
uvicorn main:app --reload
```

Server runs on: **http://localhost:8000**
- API Docs: **http://localhost:8000/docs** (Swagger)
- ReDoc: **http://localhost:8000/redoc**

## 📦 Dependencies

Core dependencies (see `requirements.txt` or `pyproject.toml`):

- **fastapi** — Modern async web framework
- **sqlmodel** — SQL ORM (SQLAlchemy + Pydantic)
- **alembic** — Database migrations
- **passlib[bcrypt]** — Password hashing
- **python-jose** — JWT token handling
- **slowapi** — Rate limiting
- **pydantic[email-validator]** — Data validation
- **httpx** — Async HTTP client (for webhooks)
- **mercadopago** — MercadoPago SDK

## 🔑 API Conventions

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
- Access tokens (JWT): Bearer token in `Authorization` header
- Refresh tokens: Stored in HTTP-only cookies or in request body
- Format: `Authorization: Bearer <access_token>`

### Response Format
All endpoints return JSON with consistent structure:

**Success (2xx):**
```json
{
  "id": 123,
  "nombre": "Product Name",
  "precio": 29.99
}
```

**Error (4xx/5xx):**
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "Invalid email format" }
  ],
  "timestamp": "2026-04-24T10:30:00Z"
}
```

### Pagination
Endpoints supporting pagination use:
- `skip`: Offset from start (default: 0)
- `limit`: Number of records to return (default: 20)

Response includes `total` count for frontend pagination.

### Rate Limiting
- **Login**: 5 attempts per IP per 15 minutes
- **Register**: 3 registrations per IP per hour
- **Order creation**: 10 per user per hour

Response headers:
- `X-RateLimit-Limit`: Total allowed requests
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## 🔒 Security

### Password Storage
- Hashed with bcrypt (cost factor ≥ 10)
- Never stored in plain text
- Rule: `RN-AU01`

### JWT Tokens
- **Access Token**: 30-minute duration, contains userId, email, roles
- **Refresh Token**: 7-day duration, opaque UUID stored in DB
- **Token Rotation**: Refresh token is revoked after use, new one issued
- **Replay Attack Detection**: Reused refresh tokens revoke all user tokens
- Rule: `RN-AU02`, `RN-AU03`, `RN-AU04`, `RN-AU05`

### CORS
- Configured from `CORS_ORIGINS` environment variable
- Defaults to `http://localhost:5173` in development
- Rule: `RN-RB10`

### Authorization
- Role-Based Access Control (RBAC): ADMIN, STOCK, PEDIDOS, CLIENT
- Verified via JWT claims
- Rule: `RN-RB01` through `RN-RB09`

## 🗄️ Database

### Connection
PostgreSQL connection via `DATABASE_URL` environment variable:
```
postgresql://user:password@localhost:5432/foodstore_dev
```

### Migrations
Managed with Alembic:
```bash
# Create new migration
alembic revision --autogenerate -m "add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Models
SQLModel models combine SQLAlchemy ORM + Pydantic validation:

```python
from sqlmodel import SQLModel, Field

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    nombre: str
    password_hash: str
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)
```

## 🛠️ Development

### Adding a New Feature

1. **Create feature directory:**
   ```bash
   mkdir backend/mi_feature
   touch backend/mi_feature/{model.py,schemas.py,repository.py,service.py,router.py}
   ```

2. **Define models** in `model.py`:
   ```python
   from sqlmodel import SQLModel, Field
   
   class MiModelo(SQLModel, table=True):
       id: int | None = Field(default=None, primary_key=True)
       # ... fields
   ```

3. **Define schemas** in `schemas.py`:
   ```python
   from pydantic import BaseModel
   
   class MiModeloCreate(BaseModel):
       # ... fields
   ```

4. **Create repository** in `repository.py`:
   ```python
   from core.patterns import BaseRepository
   
   class MiRepository(BaseRepository[MiModelo]):
       pass
   ```

5. **Add business logic** in `service.py`:
   ```python
   class MiService:
       def __init__(self, repo: MiRepository):
           self.repo = repo
   ```

6. **Register endpoints** in `router.py`:
   ```python
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix="/api/v1/mi-feature", tags=["Mi Feature"])
   
   @router.get("/")
   async def listar():
       # ...
   ```

7. **Import router in main.py:**
   ```python
   from mi_feature.router import router
   app.include_router(router)
   ```

### Code Style
- Follow PEP 8
- Type hints on all functions
- Docstrings on public functions
- Use meaningful variable names

### Testing
(To be implemented)
- Unit tests in `tests/` directory
- Run: `pytest`
- Coverage: `pytest --cov`

## 🚨 Troubleshooting

### Database Connection Error
```
Error: could not connect to server: Connection refused
```
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify credentials and database exists

### Migration Error
```
Error: Target database is not up to date
```
```bash
alembic upgrade head
```

### Import Error: "No module named 'core'"
- Ensure you're running from the `backend/` directory
- Check that `backend/` is in Python path
- Or run: `export PYTHONPATH=$PYTHONPATH:.`

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Food Store Architecture Decision Records](./docs/adr/) (if applicable)
