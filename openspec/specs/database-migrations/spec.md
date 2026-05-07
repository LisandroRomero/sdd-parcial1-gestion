## ADDED Requirements

### Requirement: Migración Alembic 0002_create_all_tables

El sistema SHALL generar una migración Alembic `0002_create_all_tables.py` vía autogenerate (`alembic revision --autogenerate -m "create_all_tables"`) que refleje exactamente los modelos SQLModel definidos, creando las 15 tablas con todos sus constraints (PK, FK, UQ, CHECK, NOT NULL) y tipos de datos correctos.

#### Scenario: Autogenerate captura todas las tablas
- **WHEN** se ejecuta `alembic revision --autogenerate -m "create_all_tables"`
- **THEN** SHALL generar operaciones CREATE TABLE para: usuario, rol, usuariorol, refreshtoken, direccionentrega, categoria, producto, productocategoria, ingrediente, productoingrediente, formapago, estadopedido, pedido, detallepedido, historialestadopedido, pago

#### Scenario: Autogenerate captura PK compuestas
- **WHEN** se revisa la migración generada
- **THEN** SHALL incluir PrimaryKeyConstraint para usuariorol (usuario_id, rol_codigo), productocategoria (producto_id, categoria_id), productoingrediente (producto_id, ingrediente_id)

#### Scenario: Autogenerate captura FK
- **WHEN** se revisa la migración generada
- **THEN** SHALL incluir ForeignKeyConstraint para todas las relaciones entre tablas (ej: pedido.usuario_id → usuario.id, detallepedido.pedido_id → pedido.id, etc.)

#### Scenario: Autogenerate captura tipos ARRAY
- **WHEN** se revisa la migración para DetallePedido
- **THEN** SHALL verificar que el campo personalizacion use SQLAlchemy ARRAY(Integer) y no VARCHAR u otro tipo incorrecto

### Requirement: Revisión manual de la migración autogenerada

El sistema SHALL requerir revisión y corrección manual de la migración autogenerada antes de ser ejecutada, especialmente para tipos que Alembic pueda malinterpretar (ARRAY, DECIMAL con precisión, TIMESTAMPTZ).

#### Scenario: Corrección de tipos si es necesario
- **WHEN** la migración autogenerada no captura correctamente ARRAY(INTEGER) o DECIMAL(10,2)
- **THEN** SHALL corregir manualmente la migración antes de ejecutar `alembic upgrade head`

### Requirement: Ejecución y verificación de migración

El sistema SHALL ejecutar `alembic upgrade head` y verificar que las tablas se crearon correctamente conectándose a la BD y consultando el schema.

#### Scenario: Migración exitosa
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** SHALL crear todas las tablas sin errores y `alembic current` SHALL mostrar la revisión más reciente
