## 1. Bootstrap de aplicación y routing

- [x] 1.1 Crear entrypoint del backend (`backend/main.py` o convención equivalente) con `app = FastAPI(...)`
- [x] 1.2 Crear router agregador versionado (p.ej. `backend/api/v1/router.py`) y montar en `/api/v1`
- [x] 1.3 Definir healthcheck mínimo (`GET /api/v1/health`) para validar que la app corre

## 2. Configuración por entorno

- [x] 2.1 Implementar `backend/core/config.py` con Settings tipadas (env + `.env`) y defaults seguros
- [x] 2.2 Agregar `backend/.env.example` con variables requeridas (DB, JWT placeholders, CORS, MercadoPago placeholders)
- [x] 2.3 Conectar el entrypoint para cargar Settings y configurar CORS desde `CORS_ORIGINS`

## 3. Base de datos (SQLModel) + Unit of Work

- [x] 3.1 Implementar `backend/core/database.py` con `engine` y factory de `Session`
- [x] 3.2 Implementar dependencia `get_session()` (por request) para uso en routers/repositorios
- [x] 3.3 Implementar `backend/core/uow.py` mínimo (session + commit/rollback) y documentar el patrón de uso

## 4. Alembic (migraciones)

- [x] 4.1 Inicializar/configurar Alembic para PostgreSQL y SQLModel `metadata` (target_metadata)
- [x] 4.2 Definir estructura esperada de migraciones (`backend/alembic/` y `versions/`) y comando de ejecución en docs
- [x] 4.3 Crear una migración “baseline” (vacía o inicial) y verificar que `alembic upgrade head` funciona contra una DB local

## 5. Documentación y DX

- [x] 5.1 Actualizar `backend/README.md` para reflejar comandos reales (dependencias, server, migraciones) según lo implementado
- [x] 5.2 (Opcional) Agregar `docker-compose.yml` para PostgreSQL local y documentar su uso
