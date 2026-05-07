## Why

El proyecto Food Store necesita una base de datos funcional para operar. Actualmente existe toda la infraestructura base (conexión a PostgreSQL 16, UnitOfWork, Alembic configurado, Docker Compose con la base de datos) pero **cero tablas definidas**, **cero modelos SQLModel** y **cero datos semilla**. Sin esto, ningún módulo del backend puede operar — no hay usuarios, productos, pedidos ni pagos.

Este change es el **bloque fundacional** (Sprint 0, ID 0.3) que permite que los módulos de negocio (auth, usuarios, productos, pedidos, pagos) empiecen a funcionar sobre datos reales.

## What Changes

- **Modelos SQLModel** para las 15 entidades del ERD v5 en todos los módulos backend
- **Migración Alembic** (`0002_create_all_tables.py`) autogenerada desde los modelos
- **Schemas Pydantic** Create/Update/Read para cada entidad
- **Script de seed** con datos iniciales obligatorios (catálogos fijos + usuario admin)
- **Dependencias** agregadas al backend (sqlmodel, alembic, psycopg, passlib, etc.) si no existen en `requirements.txt`

## Capabilities

### New Capabilities

- `database-models`: Modelos SQLModel para las 15 entidades del ERD v5 distribuidas en los 7 módulos backend (usuarios, productos, categorias, ingredientes, pedidos, pagos, direcciones, refreshtokens) con tipos correctos, constraints, relaciones, campos de auditoría, soft-delete y snapshot pattern
- `pydantic-schemas`: Schemas Pydantic Create/Update/Read para cada entidad, con validaciones de negocio (email, precio, stock) y tipos correctos (DECIMAL, VARCHAR, BOOLEAN, INTEGER[])
- `database-migrations`: Migración Alembic autogenerada `0002_create_all_tables.py` que refleja fielmente los modelos SQLModel definidos
- `database-seed`: Script de seed con catálogos fijos (4 roles, 6 estados de pedido, 3 formas de pago) y usuario administrador inicial

### Modified Capabilities

- *(ninguna — es la primera vez que se definen modelos de datos)*

## Impact

- **Backend**: Todos los módulos (`auth/`, `usuarios/`, `productos/`, `categorias/`, `ingredientes/`, `pedidos/`, `pagos/`, `direcciones/`, `refreshtokens/`) reciben modelos y schemas concretos
- **Base de datos**: PostgreSQL 16 con migration `0002_create_all_tables.py` que crea las 15 tablas del ERD v5
- **Dependencias**: Se agregarán sqlmodel, alembic, psycopg[binary], passlib[bcrypt], pydantic[email-validator] al backend
- **Docker**: Sin cambios — el `docker-compose.yml` ya levanta PostgreSQL 16 correctamente
- **Documentación**: Sin cambios directos, pero desbloquea la implementación de todos los módulos de negocio
