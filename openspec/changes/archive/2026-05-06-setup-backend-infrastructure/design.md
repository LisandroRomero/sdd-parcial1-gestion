## Context

El repo ya define la arquitectura target del backend (FastAPI + SQLModel + PostgreSQL + Alembic) y un layout feature-first (router → service → uow → repository → model). Sin embargo, todavía no existe un “runnable backend”: faltan entrypoint, configuración por entorno, wiring de DB/sesión, manejo de errores transversal y una configuración consistente de migraciones.

Esto bloquea el desarrollo iterativo: cada feature terminaría resolviendo infraestructura “a su manera”, generando deuda técnica y divergencias.

## Goals / Non-Goals

**Goals:**

- Definir un **entrypoint único** del backend (FastAPI app) con configuración de middleware y registro de routers por versión (`/api/v1`).
- Centralizar configuración por entorno en `backend/core/config.py` (Pydantic settings) y estandarizar `.env.example`.
- Proveer infraestructura de DB:
  - `engine`/`Session` (SQLModel/SQLAlchemy)
  - dependencia `get_session()` para routers
  - base de Unit of Work en `backend/core/uow.py`
- Configurar **Alembic** para SQLModel + PostgreSQL, con un flujo claro: generar revision → aplicar → rollback.
- Dejar listas convenciones mínimas para:
  - manejo consistente de errores (HTTPException desde service)
  - logging básico
  - CORS (desde env)

**Non-Goals:**

- Implementar lógica de negocio (auth/productos/pedidos/etc.).
- Implementar CI/CD, testing, linting o pre-commit hooks (pueden ser changes posteriores).
- Definir seguridad completa (JWT/RBAC) más allá de placeholders de config.

## Decisions

1) **Entry point y composición de la app**

- **Decisión**: Crear un `backend/main.py` (o `backend/app.py`) que exponga `app = FastAPI(...)` y un `backend/api/v1/router.py` agregador.
- **Rationale**: separa composición (wiring) de features; evita imports cruzados y permite versionado de API.
- **Alternativas**:
  - “Cada feature se auto-registra”: simple al inicio, pero rompe claridad y facilita ciclos de imports.

2) **Configuración por entorno con Settings**

- **Decisión**: Usar Pydantic Settings (v2 si el proyecto lo define; caso contrario, v1) en `backend/core/config.py` con lectura de `.env`.
- **Rationale**: tipado, defaults seguros, configuración central y validación temprana.
- **Alternativas**:
  - `os.environ` disperso: rápido, pero sin validación y difícil de testear.

3) **DB: SQLModel + Session por request**

- **Decisión**: Implementar `engine` singleton + `Session` por request vía dependencia `get_session()`.
- **Rationale**: patrón estándar con FastAPI; aislación por request; compatible con UoW.
- **Alternativas**:
  - sesión global: peligroso y propenso a errores de concurrencia.

4) **Alembic “source of truth”**

- **Decisión**: Configurar Alembic para usar `target_metadata` basado en SQLModel y hacer migraciones explícitas con revisiones versionadas.
- **Rationale**: trazabilidad de cambios en schema y control de despliegue/rollback.
- **Alternativas**:
  - `create_all()` en runtime: sirve para demos, no para un equipo ni producción.

5) **CORS y middlewares**

- **Decisión**: CORS configurado por env (`CORS_ORIGINS`) y middlewares globales en el entrypoint.
- **Rationale**: seguridad por default y comportamiento consistente.
- **Alternativas**:
  - CORS hardcodeado: frágil y no portable.

## Risks / Trade-offs

- **[Riesgo] Pydantic v1 vs v2** → **Mitigación**: inspeccionar dependencias existentes (si hay) y fijar una sola versión en el manifiesto; documentar.
- **[Riesgo] Alembic autogenerate incorrecto** (relaciones/nullable/defaults) → **Mitigación**: revisar revisiones generadas, agregar comentarios y tests de migración básicos en un change posterior.
- **[Trade-off] Introducir UoW temprano** aumenta boilerplate → **Mitigación**: mantener UoW mínimo (session + commit/rollback) y crecer cuando aparezcan casos reales.
