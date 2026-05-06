## Why

El repo tiene la estructura del backend definida (feature-first + core), pero hoy faltan piezas de infraestructura para **correr** la API y trabajar en equipo (bootstrap de la app, configuración por entorno, conexión a PostgreSQL y migraciones). Sin esto, no se pueden implementar features de negocio de forma consistente ni reproducible.

## What Changes

- Se agrega el **bootstrap del backend** (FastAPI app + routing base) y la infraestructura mínima en `backend/core/` (config/env, DB session/engine, dependencias comunes, manejo de errores/logging).
- Se incorpora **migraciones** (Alembic) configuradas para SQLModel/PostgreSQL y un flujo de ejecución local reproducible.
- Se agregan **assets de entorno de desarrollo**: `backend/.env.example` y (si aplica) `docker-compose.yml` para PostgreSQL local.
- Se documenta el flujo de ejecución (actualizando `backend/README.md` si hiciera falta) para que el setup sea “clonar y correr”.

## Capabilities

### New Capabilities
- `backend-infrastructure`: Infraestructura base del backend para desarrollo local (configuración, app bootstrap, DB, migraciones, logging/errores) lista para soportar features.

### Modified Capabilities

<!-- none -->

## Impact

- **Código**: afecta principalmente `backend/` (nuevo `main.py`/`app.py` según convención, `backend/core/*`, módulos para integración Alembic).
- **Infra**: agrega/ajusta configuración de entorno (`backend/.env.example`) y potencialmente `docker-compose.yml` para DB.
- **Dependencias**: define el manejo de dependencias Python (Poetry o pip/requirements) y versiones mínimas.
- **DX**: habilita que cualquier dev pueda levantar API + DB y correr migraciones con pasos claros.
