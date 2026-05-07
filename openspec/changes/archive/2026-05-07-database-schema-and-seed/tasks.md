## 1. Dependencias y Setup

- [x] 1.1 Agregar sqlmodel, alembic, psycopg[binary], passlib[bcrypt], pydantic[email-validator] a backend/requirements.txt
- [x] 1.2 Verificar que docker-compose.yml tenga PostgreSQL 16 configurado y funcional

## 2. Modelos SQLModel — Dominio Identidad y Acceso

- [x] 2.1 Implementar modelo Usuario en backend/usuarios/model.py (email VARCHAR(254) UQ, password_hash CHAR(60), nombre, apellido, telefono, activo, deleted_at, created_at, updated_at)
- [x] 2.2 Implementar modelo Rol en backend/usuarios/model.py (codigo VARCHAR(20) PK, descripcion TEXT)
- [x] 2.3 Implementar modelo UsuarioRol en backend/usuarios/model.py (PK compuesta usuario_id + rol_codigo, asignado_por_id FK)
- [x] 2.4 Implementar modelo RefreshToken en backend/refreshtokens/model.py (token_hash CHAR(64) UQ, usuario_id FK, expires_at, revoked_at nullable, created_at)
- [x] 2.5 Implementar modelo DireccionEntrega en backend/direcciones/model.py (usuario_id FK, alias, linea1, linea2 nullable, ciudad, codigo_postal, es_principal BOOLEAN, created_at, updated_at)

## 3. Modelos SQLModel — Dominio Catálogo

- [x] 3.1 Implementar modelo Categoria en backend/categorias/model.py (parent_id FK self-referencial nullable, nombre, descripcion, deleted_at, created_at, updated_at)
- [x] 3.2 Implementar modelo Producto en backend/productos/model.py (codigo_sku UQ, nombre, descripcion, precio_base DECIMAL(10,2), stock_cantidad INT, disponible BOOLEAN, imagen_url, deleted_at, created_at, updated_at)
- [x] 3.3 Implementar modelo Ingrediente en backend/ingredientes/model.py (nombre VARCHAR(100) UQ, es_alergeno BOOLEAN, created_at)
- [x] 3.4 Implementar modelo ProductoCategoria en backend/productos/model.py (PK compuesta producto_id + categoria_id, es_principal BOOLEAN)
- [x] 3.5 Implementar modelo ProductoIngrediente en backend/ingredientes/model.py (PK compuesta producto_id + ingrediente_id, es_removible BOOLEAN)

## 4. Modelos SQLModel — Dominio Ventas y Pagos

- [x] 4.1 Implementar modelo FormaPago en backend/pagos/model.py (codigo VARCHAR(20) PK, descripcion TEXT)
- [x] 4.2 Implementar modelo EstadoPedido en backend/pedidos/model.py (codigo VARCHAR(20) PK, descripcion TEXT, es_terminal BOOLEAN)
- [x] 4.3 Implementar modelo Pedido en backend/pedidos/model.py (usuario_id FK, forma_pago_codigo FK, direccion_id FK, estado_actual FK, total DECIMAL(10,2), costo_envio DECIMAL(10,2), created_at, updated_at)
- [x] 4.4 Implementar modelo DetallePedido en backend/pedidos/model.py (pedido_id FK, producto_id FK, nombre_snapshot, precio_snapshot DECIMAL, cantidad INT, personalizacion ARRAY(INTEGER), subtotal DECIMAL)
- [x] 4.5 Implementar modelo HistorialEstadoPedido en backend/pedidos/model.py (pedido_id FK, estado_desde nullable, estado_hasta, created_at) — append-only
- [x] 4.6 Implementar modelo Pago en backend/pagos/model.py (pedido_id FK, mp_payment_id BIGINT UQ, mp_status VARCHAR(30), external_reference UUID UQ, idempotency_key UUID UQ, monto DECIMAL(10,2), moneda VARCHAR(3), created_at, updated_at)

## 5. Schemas Pydantic

- [x] 5.1 Implementar schemas UsuarioCreate/Update/Read, RolCreate/Read, UsuarioRolCreate/Read en backend/usuarios/schemas.py
- [x] 5.2 Implementar schemas RefreshTokenCreate/Read en backend/refreshtokens/schemas.py
- [x] 5.3 Implementar schemas DireccionEntregaCreate/Update/Read en backend/direcciones/schemas.py
- [x] 5.4 Implementar schemas CategoriaCreate/Update/Read en backend/categorias/schemas.py
- [x] 5.5 Implementar schemas ProductoCreate/Update/Read, ProductoCategoriaCreate/Read en backend/productos/schemas.py
- [x] 5.6 Implementar schemas IngredienteCreate/Update/Read, ProductoIngredienteCreate/Read en backend/ingredientes/schemas.py
- [x] 5.7 Implementar schemas PedidoCreate/Update/Read, DetallePedidoCreate/Read en backend/pedidos/schemas.py
- [x] 5.8 Implementar schemas PagoCreate/Read en backend/pagos/schemas.py

## 6. Migración Alembic

- [x] 6.1 Ejecutar `alembic revision --autogenerate -m "create_all_tables"` para generar migración 0002
- [x] 6.2 Revisar y corregir manualmente la migración autogenerada (verificar tipos ARRAY, DECIMAL, TIMESTAMPTZ, PK compuestas, FK)
- [x] 6.3 Ejecutar `alembic upgrade head` y verificar que las tablas se crearon correctamente

## 7. Seed Data

- [x] 7.1 Crear directorio backend/scripts/ y archivo seed.py con lógica idempotente
- [x] 7.2 Implementar seed de roles (ADMIN, STOCK, PEDIDOS, CLIENT) con verificación de existencia previa
- [x] 7.3 Implementar seed de estados de pedido (PENDIENTE, CONFIRMADO, PREPARACION, ENVIADO, ENTREGADO, CANCELADO) con es_terminal en ENTREGADO y CANCELADO
- [x] 7.4 Implementar seed de formas de pago (MERCADOPAGO, EFECTIVO, TRANSFERENCIA)
- [x] 7.5 Implementar seed de usuario admin (admin@foodstore.com / Admin1234!) con rol ADMIN y password hasheado con bcrypt cost >= 12
- [x] 7.6 Verificar idempotencia: ejecutar seed dos veces sin generar duplicados

## 8. Verificación Final

- [x] 8.1 Verificar que todas las tablas existen y tienen datos esperados (roles, estados, formas de pago, admin)
- [x] 8.2 Verificar que alembic current muestra la revisión más reciente
- [x] 8.3 Verificar que los schemas Pydantic compilan y validan correctamente con datos de prueba
