## ADDED Requirements

### Requirement: Seed de catálogos fijos (Roles)

El sistema SHALL incluir un script de seed que inserte los 4 roles del sistema: ADMIN (Administrador general), STOCK (Gestor de Stock), PEDIDOS (Gestor de Pedidos), CLIENT (Cliente).

#### Scenario: Roles predefinidos
- **WHEN** se ejecuta el seed
- **THEN** SHALL existir registros en tabla rol con codigos ADMIN, STOCK, PEDIDOS, CLIENT

### Requirement: Seed de catálogos fijos (Estados de Pedido)

El sistema SHALL incluir un script de seed que inserte los 6 estados del FSM de pedidos: PENDIENTE, CONFIRMADO, PREPARACION, ENVIADO, ENTREGADO (terminal), CANCELADO (terminal).

#### Scenario: Estados de pedido con terminales
- **WHEN** se ejecuta el seed
- **THEN** SHALL existir registros en tabla estadopedido con los 6 estados, donde ENTREGADO y CANCELADO tengan es_terminal = True

### Requirement: Seed de catálogos fijos (Formas de Pago)

El sistema SHALL incluir un script de seed que inserte las 3 formas de pago: MERCADOPAGO (Mercado Pago), EFECTIVO (Efectivo), TRANSFERENCIA (Transferencia Bancaria).

#### Scenario: Formas de pago predefinidas
- **WHEN** se ejecuta el seed
- **THEN** SHALL existir registros en tabla formapago con codigos MERCADOPAGO, EFECTIVO, TRANSFERENCIA

### Requirement: Seed de usuario administrador inicial

El sistema SHALL crear un usuario administrador inicial con email `admin@foodstore.com`, password hasheado con bcrypt (cost factor >= 12) que cumpla `Admin1234!`, nombre "Admin", apellido "FoodStore", y asignarle el rol ADMIN.

#### Scenario: Admin login funcional
- **WHEN** se ejecuta el seed
- **THEN** SHALL existir un usuario con email admin@foodstore.com, password hasheado, y un registro en usuariorol asignándole el rol ADMIN

### Requirement: Script de seed ejecutable e idempotente

El sistema SHALL proveer un script `backend/scripts/seed.py` ejecutable vía `python -m backend.scripts.seed` que sea idempotente (verificar existencia antes de insertar para evitar duplicados al ejecutarlo múltiples veces).

#### Scenario: Idempotencia del seed
- **WHEN** se ejecuta el seed dos veces
- **THEN** la segunda ejecución NO SHALL crear duplicados de roles, estados, formas de pago ni usuario admin
