## Context

El módulo `auth/` está completamente vacío (5 archivos sin contenido). `usuarios/` tiene el modelo `Usuario` SQLModel y los schemas Pydantic (`UsuarioCreate`, `UsuarioRead`, `UsuarioUpdate`) pero no tiene repository, service ni router. `refreshtokens/` tiene model y schemas pero tampoco repository/service/router.

En cambio, `core/` está completo: `BaseRepository[T]` genérico con soft-delete, `UnitOfWork` con context manager y `_ReposRegistry` lazy, `security.py` con bcrypt (costo 12) + JWT create/verify, `dependencies.py` con `get_current_user()`, `require_role()` y `get_uow()`). Todo listo para consumir.

La base de datos ya tiene las tablas `usuario`, `rol` y `usuario_rol` migradas. El seed data debe proveer el rol `CLIENT`.

## Goals / Non-Goals

**Goals:**
- Endpoint `POST /api/v1/auth/register` funcional, probable vía Swagger UI
- Validación de datos de entrada (nombre, apellido, email, password)
- Unicidad de email verificada en la capa de servicio
- Password hasheado con bcrypt (costo ≥ 12)
- Asignación automática del rol `CLIENT` al nuevo usuario
- Todo en una sola transacción atómica (UoW)
- Response `201 Created` con `UserResponse` (sin tokens)

**Non-Goals:**
- Auto-login después del registro (el usuario debe loguearse por separado)
- Endpoints de login, refresh, logout, me (cambio separado)
- Frontend de registro (cambio separado)
- Rate limiting en /register (solo cubriremos /login cuando se implemente)
- Verificación de email (out of scope para v1)
- CRUD de usuarios por parte de administradores (es del módulo `usuarios/`, cambio separado)

## Decisions

### 1. Auth service usa UsuarioRepository directamente

**Decisión**: `auth/service.py` recibe el `UnitOfWork` y accede a `uow.repos.usuarios` directamente, sin pasar por un `usuarios/service.py`.

**Alternativa considerada**: Crear `usuarios/service.py` como intermediario.

**Razón**: Para este cambio, agregar una capa de servicio en usuarios solo añade indirección sin beneficio. El registro es una operación simple: crear usuario + asignar rol. Cuando se implemente el CRUD de usuarios (módulo `usuarios/`), ese módulo tendrá su propio service con lógica más compleja. En ese momento se puede refactorizar sin romper nada porque `UsuarioRepository` ya existe.

### 2. Registro centralizado de repos en dependencies.py

**Decisión**: Los repositorios se registran en `_ReposRegistry` una sola vez, al crear el UoW, vía una función `_register_repos()` en `dependencies.py`.

**Alternativa considerada**: Registrar repos en cada router al usarlos.

**Razón**: Las factories son lazy (el repo se instancia solo al primer acceso), no hay overhead. Un solo lugar de registro evita duplicación y errores. Coincide con cómo está diseñado `_ReposRegistry` en `uow.py`.

### 3. RegisterRequest vs UsuarioCreate

**Decisión**: Se crea `RegisterRequest` en `auth/schemas.py` con `nombre`, `apellido`, `email` (EmailStr) y `password` (str, min 8). Es un schema específico para registro, separado del `UsuarioCreate` que ya existe en `usuarios/schemas.py`.

**Razón**: `UsuarioCreate` tiene `telefono` como campo opcional que no pertenece al registro. Mantener schemas separados por contexto es más limpio y evita acoplar el registro al módulo de usuarios. `UserResponse` se usa como respuesta.

### 4. Respuesta 201 sin auto-login

**Decisión**: El endpoint retorna `201 Created` con `UserResponse` (id, nombre, apellido, email, roles, created_at). No se generan tokens.

**Razón**: La spec (sección 5.1) define explícitamente `201 UserResponse`. El login es un paso separado. Esto mantiene la semántica REST pura y evita sorpresas.

### 5. Asignación de rol CLIENT en la misma transacción

**Decisión**: Dentro del mismo `UnitOfWork`, después de crear el `Usuario`, se crea el registro `UsuarioRol` con `rol_codigo="CLIENT"`. Si algo falla, el rollback del UoW revierte ambas operaciones.

**Razón**: Un usuario no debería existir sin un rol — dejaría el sistema en estado inconsistente. La atomicidad del UoW garantiza que usuario y rol se crean juntos o no se crea ninguno.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **Race condition en email único**: Dos requests simultáneos con el mismo email podrían pasar la validación antes de que el primero haga commit | La constraint UNIQUE en la columna `email` de la BD es la última línea de defensa. Si ocurre, el commit del UoW lanzará un integrity error que se propaga como HTTP 409. |
| **Password en logs**: Si se loguea el body del request, el password queda expuesto | FastAPI no loguea bodies por defecto en producción. Verificar que no haya middlewares de logging que capturen requests completos. |
| **Rol CLIENT no existe en seed**: Si el seed no se ejecutó, el registro falla por violación de FK | El error de integridad es claro y se propaga. El seed es obligatorio (spec sección 10.2). |
| **Sin rate limiting**: El endpoint /register puede ser abusado para crear cuentas masivamente | Se documenta como limitación. Se abordará en un cambio futuro de rate limiting global. |
