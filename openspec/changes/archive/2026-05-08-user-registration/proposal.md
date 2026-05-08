## Why

El sistema Food Store necesita que los nuevos usuarios puedan crear una cuenta para acceder al catálogo, gestionar su carrito y realizar pedidos. Actualmente no existe ningún endpoint de registro — los módulos `auth/` y `usuarios/` tienen models y schemas pero sus routers, services y repositories están vacíos. Sin registro, el sistema es inaccesible para clientes nuevos.

## What Changes

- Se crea el endpoint `POST /api/v1/auth/register` que permite a un nuevo usuario registrarse con nombre, apellido, email y password
- Se crea `UsuarioRepository` en `usuarios/repository.py` con el método `get_by_email()` para validar unicidad
- Se crean los schemas `RegisterRequest` y `UserResponse` en `auth/schemas.py`
- Se crea `auth/service.py` con la lógica de registro: validar email único, hashear password, crear usuario con rol CLIENT, todo dentro de una transacción UoW
- Se crea `auth/router.py` con el endpoint POST /register
- Se actualiza `api/v1/router.py` para incluir el router de auth
- Se implementa el registro centralizado de repositorios en el UoW (vía `dependencies.py`)
- No incluye auto-login (el usuario debe loguearse explícitamente después del registro)
- No incluye frontend ni otros endpoints de auth (login, refresh, logout, me — serán cambios separados)

## Capabilities

### New Capabilities

- `user-registration`: Capacidad del sistema para registrar nuevos usuarios clientes. Incluye validación de datos, unicidad de email, hashing de contraseña y asignación automática del rol CLIENT.

### Modified Capabilities

Ninguna. No se modifican capabilities existentes.

## Impact

- **Backend**: Se implementan los módulos `auth/` (router, service, schemas) y se completa `usuarios/repository.py`
- **API**: Nuevo endpoint `POST /api/v1/auth/register` bajo prefijo `/api/v1`
- **Dependencias**: Se agrega registro de `UsuarioRepository` en el UnitOfWork vía `backend/api/v1/dependencies.py`
- **Base de datos**: Las tablas `usuario`, `rol` y `usuario_rol` ya existen via migrations — no se requieren nuevas migraciones. El seed data debe tener el rol CLIENT creado.
- No afecta frontend, no afecta otros módulos del backend.
