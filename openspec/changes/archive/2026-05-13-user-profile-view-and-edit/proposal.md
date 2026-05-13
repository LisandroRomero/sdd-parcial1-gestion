## Why

Los usuarios autenticados actualmente pueden consultar su perfil básico a través de `GET /api/v1/auth/me`, pero ese endpoint retorna un snapshot mínimo (sin `telefono`, sin `apellido` en forma editable, sin direcciones de entrega activas) y no ofrece ningún mecanismo para que el propio usuario edite sus datos. Para completar el ciclo de autogestión del perfil (Epic 3.2), se necesita un endpoint dedicado en el dominio `usuarios/` que exponga un perfil enriquecido y permita actualizaciones seguras.

## What Changes

- Nuevo endpoint `GET /api/v1/usuarios/me/perfil` que retorna el perfil completo del usuario autenticado: `id`, `nombre`, `apellido`, `email`, `telefono`, `roles`, `activo`, `created_at` + lista de `DireccionEntregaRead` activas (sin `deleted_at`).
- Nuevo endpoint `PUT /api/v1/usuarios/me/perfil` que permite al usuario editar exclusivamente `nombre`, `apellido` y `telefono`; email, roles y password quedan fuera de este flujo.
- Dos nuevos schemas Pydantic en `backend/usuarios/schemas.py`: `PerfilRead` y `PerfilUpdate`.
- El campo `telefono` **ya existe** en el modelo `Usuario` (`Optional[str]`, `max_length=20`) — no se requiere migración de base de datos.
- El campo `apellido` **ya existe** en el modelo `Usuario` — se incluirá en `PerfilUpdate` además de `nombre` y `telefono`.
- Nueva función de servicio `get_perfil` y `update_perfil` en `backend/usuarios/service.py`.
- Los nuevos endpoints se registran en `backend/usuarios/router.py` bajo el prefijo `/me/perfil`.
- `GET /api/v1/auth/me` existente **no se modifica** — sigue siendo el endpoint de identidad ligera para uso de auth; el nuevo endpoint complementa con datos de perfil enriquecido.

## Capabilities

### New Capabilities

- `user-profile-management`: Permite a cualquier usuario autenticado ver y editar su propio perfil (nombre, apellido, teléfono), incluyendo sus direcciones de entrega activas en la vista. No expone ni permite modificar campos sensibles como email, roles ni password.

### Modified Capabilities

<!-- No se modifica ninguna spec existente. El endpoint GET /api/v1/auth/me (auth-me) no cambia su contrato. -->

## Impact

- **Código afectado:** `backend/usuarios/schemas.py`, `backend/usuarios/service.py`, `backend/usuarios/router.py`
- **Sin migraciones:** el modelo `Usuario` ya tiene `nombre`, `apellido`, `telefono`; no hay cambios de esquema en la BD.
- **Depende de:** `DireccionEntrega` (Epic 3.1) para incluir direcciones activas en `PerfilRead`; `get_current_user` de `backend/core/dependencies.py` para autenticación.
- **No rompe contratos existentes:** `GET /api/v1/auth/me` y `PUT /{id}/roles` no se alteran.
- **Roles:** los nuevos endpoints son accesibles para cualquier usuario autenticado (sin restricción de rol).
