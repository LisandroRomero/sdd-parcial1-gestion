## ADDED Requirements

### Requirement: Modelos SQLModel para Usuario, Rol y UsuarioRol

El sistema SHALL definir los modelos SQLModel para el dominio de identidad y acceso en `backend/usuarios/model.py`, incluyendo Usuario (con email único, password_hash CHAR(60), soft-delete deleted_at), Rol (con PK semántica VARCHAR(20): ADMIN, STOCK, PEDIDOS, CLIENT), y UsuarioRol (PK compuesta usuario_id + rol_codigo, con asignado_por_id).

#### Scenario: Usuario tiene campos obligatorios y soft-delete
- **WHEN** se define el modelo Usuario
- **THEN** SHALL incluir: id (autoincremental), email (VARCHAR(254) UNIQUE NOT NULL), password_hash (CHAR(60) NOT NULL), nombre (VARCHAR(100)), apellido (VARCHAR(100)), telefono (VARCHAR(20)), activo (BOOLEAN default True), created_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ), deleted_at (TIMESTAMPTZ nullable)

#### Scenario: Rol usa PK semántica
- **WHEN** se define el modelo Rol
- **THEN** SHALL usar codigo VARCHAR(20) como primary key, con columna descripcion TEXT

#### Scenario: UsuarioRol usa PK compuesta
- **WHEN** se define UsuarioRol
- **THEN** SHALL tener PK compuesta (usuario_id, rol_codigo) y FK a usuario_id (con ondelete=CASCADE) y rol_codigo, más columna asignado_por_id FK a Usuario

### Requirement: Modelo RefreshToken

El sistema SHALL definir el modelo RefreshToken en `backend/refreshtokens/model.py` con token_hash CHAR(64) UNIQUE, FK a usuario_id, expires_at, revoked_at nullable, created_at TIMESTAMPTZ.

#### Scenario: RefreshToken soporta revocación lógica
- **WHEN** se crea un RefreshToken
- **THEN** SHALL tener token_hash único, FK al usuario, expires_at requerido, revoked_at nullable (NULL = activo, valor = revocado)

### Requirement: Modelo DireccionEntrega

El sistema SHALL definir el modelo DireccionEntrega en `backend/direcciones/model.py` con FK a usuario_id, alias VARCHAR(50), linea1 TEXT, linea2 TEXT nullable, ciudad VARCHAR(100), codigo_postal VARCHAR(20), es_principal BOOLEAN default False, created_at, updated_at.

#### Scenario: DireccionEntrega pertenece a un usuario
- **WHEN** se crea una dirección
- **THEN** SHALL tener FK a usuario_id y solo un campo es_principal = True por usuario

### Requirement: Modelo Categoria (jerárquico)

El sistema SHALL definir el modelo Categoria en `backend/categorias/model.py` con parent_id FK self-referencial nullable, soft-delete deleted_at, created_at, updated_at.

#### Scenario: Categoria soporta jerarquía
- **WHEN** se define Categoria
- **THEN** SHALL tener parent_id nullable FK a la misma tabla, con soft-delete y timestamps de auditoría

### Requirement: Modelo Producto

El sistema SHALL definir el modelo Producto en `backend/productos/model.py` con precio_base DECIMAL(10,2), stock_cantidad INT, disponible BOOLEAN, soft-delete, created_at, updated_at.

#### Scenario: Producto tiene precio y stock
- **WHEN** se define Producto
- **THEN** SHALL incluir: codigo_sku VARCHAR(50) UNIQUE, nombre VARCHAR(200), descripcion TEXT, precio_base DECIMAL(10,2) NOT NULL, stock_cantidad INT NOT NULL default 0, disponible BOOLEAN default True, imagen_url TEXT, deleted_at nullable, created_at, updated_at

### Requirement: Modelo Ingrediente

El sistema SHALL definir el modelo `Ingrediente` en `backend/ingredientes/model.py` con los campos: `nombre VARCHAR(100) UNIQUE NOT NULL`, `es_alergeno BOOLEAN NOT NULL DEFAULT false`, `created_at TIMESTAMPTZ DEFAULT now()`, y `deleted_at TIMESTAMPTZ NULL` para soft delete.

#### Scenario: Ingrediente tiene nombre único
- **WHEN** se define Ingrediente
- **THEN** SHALL tener constraint `UNIQUE` sobre `nombre`

#### Scenario: Ingrediente tiene soft delete
- **WHEN** se define Ingrediente
- **THEN** SHALL tener campo `deleted_at TIMESTAMPTZ NULL`

#### Scenario: Migración agrega columna deleted_at
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** la tabla `ingrediente` tiene la columna `deleted_at TIMESTAMPTZ NULL` sin romper filas existentes

### Requirement: Tablas N:M ProductoCategoria y ProductoIngrediente

El sistema SHALL definir las tablas pivote N:M en sus módulos correspondientes: ProductoCategoria (PK compuesta, es_principal BOOLEAN) en `backend/productos/model.py`, y ProductoIngrediente (PK compuesta, es_removible BOOLEAN) en `backend/ingredientes/model.py`.

#### Scenario: ProductoCategoria permite categoria principal
- **WHEN** se asocia un producto a una categoría
- **THEN** SHALL tener PK compuesta y campo es_principal BOOLEAN

#### Scenario: ProductoIngrediente permite ingrediente removible
- **WHEN** se asocia un ingrediente a un producto
- **THEN** SHALL tener PK compuesta y campo es_removible BOOLEAN

### Requirement: Catálogos FormaPago y EstadoPedido

El sistema SHALL definir los modelos FormaPago (codigo VARCHAR(20) PK) en `backend/pagos/model.py` y EstadoPedido (codigo VARCHAR(20) PK, es_terminal BOOLEAN) en `backend/pedidos/model.py`.

#### Scenario: FormaPago usa PK semántica
- **WHEN** se define FormaPago
- **THEN** SHALL tener codigo VARCHAR(20) PK y descripcion TEXT

#### Scenario: EstadoPedido identifica estados terminales
- **WHEN** se define EstadoPedido
- **THEN** SHALL tener codigo VARCHAR(20) PK, descripcion TEXT, es_terminal BOOLEAN default False

### Requirement: Modelo Pedido

El sistema SHALL definir el modelo Pedido en `backend/pedidos/model.py` con total DECIMAL(10,2), costo_envio DECIMAL, FK a usuario_id, FK a forma_pago_codigo, FK a direccion_id, FK a estado_actual, created_at, updated_at.

#### Scenario: Pedido tiene FK a forma de pago y dirección
- **WHEN** se define Pedido
- **THEN** SHALL incluir: usuario_id FK, forma_pago_codigo FK, direccion_id FK, total DECIMAL(10,2), costo_envio DECIMAL(10,2) default 0, estado_actual VARCHAR(20) FK a EstadoPedido, created_at, updated_at

### Requirement: Modelo DetallePedido con snapshot

El sistema SHALL definir el modelo DetallePedido en `backend/pedidos/model.py` con FK a pedido_id, FK a producto_id, nombre_snapshot VARCHAR(200), precio_snapshot DECIMAL(10,2), cantidad INT, personalizacion INTEGER[] (ARRAY), subtotal DECIMAL(10,2).

#### Scenario: DetallePedido congela nombre y precio al momento de la compra
- **WHEN** se crea un DetallePedido
- **THEN** SHALL almacenar nombre_snapshot y precio_snapshot como copia de los valores del producto al momento del pedido, no como referencia viva

#### Scenario: DetallePedido soporta personalización
- **WHEN** un detalle incluye ingredientes personalizados
- **THEN** SHALL almacenar personalizacion como ARRAY de INTEGER con IDs de ingredientes

### Requirement: Modelo HistorialEstadoPedido (append-only)

El sistema SHALL definir el modelo HistorialEstadoPedido en `backend/pedidos/model.py` con FK a pedido_id, FK a estado_desde nullable (RN-02), estado_hasta, created_at como timestamp del cambio, append-only.

#### Scenario: HistorialEstadoPedido es append-only
- **WHEN** se registra un cambio de estado
- **THEN** SHALL insertar un nuevo registro sin modificar ni eliminar registros anteriores, con FK a pedido_id y created_at automático

### Requirement: Modelo Pago

El sistema SHALL definir el modelo Pago en `backend/pagos/model.py` con mp_payment_id BIGINT UNIQUE, mp_status VARCHAR(30), external_reference UUID UNIQUE, idempotency_key UUID UNIQUE, monto DECIMAL(10,2), FK a pedido_id, created_at, updated_at.

#### Scenario: Pago tiene claves de idempotencia
- **WHEN** se crea un Pago
- **THEN** SHALL tener mp_payment_id único, external_reference único, e idempotency_key único para prevenir duplicados por la API de MercadoPago
