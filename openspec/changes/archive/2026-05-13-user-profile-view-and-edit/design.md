## Context

El módulo `backend/usuarios/` ya contiene el modelo `Usuario` completo (campos `nombre`, `apellido`, `telefono`, `email`, `activo`, `created_at`, `updated_at`, `deleted_at`) y su `UsuarioRepository`. El módulo `backend/auth/` expone `GET /api/v1/auth/me` que retorna `UserResponse` (id, nombre, apellido, email, roles, created_at) — sin teléfono ni direcciones.

El módulo `backend/direcciones/` (Epic 3.1) ya implementa `DireccionEntregaRead` y la relación `Usuario.direcciones` está declarada en el modelo.

Los nuevos endpoints viven en el mismo módulo `usuarios/` para mantener cohesión del dominio. Se evita crear un módulo separado `perfil/` porque no agrega nueva entidad de BD — solo una proyección del `Usuario` existente.

## Goals / Non-Goals

**Goals:**
- Endpoint `GET /api/v1/usuarios/me/perfil` → retorna snapshot completo del perfil autenticado.
- Endpoint `PUT /api/v1/usuarios/me/perfil` → actualiza `nombre`, `apellido`, `telefono` del usuario autenticado.
- Schemas `PerfilRead` y `PerfilUpdate` que separan la vista del perfil de los schemas admin (`UsuarioRead`, `UsuarioUpdate`).
- Validación: `nombre` y `apellido` no pueden ser string vacío (`""`); se rechaza con 422.
- Respeto del patrón `Router → Service → UoW → Repository → Model`.

**Non-Goals:**
- No incluye cambio de password (flujo propio con token de reset).
- No incluye cambio de email (requeriría verificación de unicidad + confirmación por email).
- No incluye cambio de roles (exclusivo de `PUT /{id}/roles` con rol ADMIN).
- No incluye gestión de direcciones (ya existe en `backend/direcciones/`).
- No modifica `GET /api/v1/auth/me` ni `UserResponse`.

## Decisions

### D1 — Schemas específicos `PerfilRead` / `PerfilUpdate` vs. reusar `UsuarioRead`

`UsuarioRead` no incluye `roles`, `apellido` ni `direcciones`. Extenderlo mezclaría conceptos admin (incluye `updated_at` pero no roles) con la vista de perfil. Se crean schemas dedicados que expresan explícitamente el contrato del perfil.

**Alternativa descartada:** heredar de `UsuarioRead` — acopla la vista de perfil a cambios del schema admin.

### D2 — Incluir direcciones activas en `PerfilRead`

Las direcciones activas (sin `deleted_at`) son parte natural del perfil de entrega. Se incluyen directamente en `PerfilRead` como `list[DireccionEntregaRead]` usando la relación `Usuario.direcciones` ya existente.

**Carga:** dado que la lista de direcciones de un usuario típico es pequeña (< 10), un JOIN eager es aceptable sin paginación adicional.

**Alternativa descartada:** endpoint separado para direcciones — ya existe `GET /api/v1/usuarios/me/direcciones` (Epic 3.1); `PerfilRead` las embebe como conveniencia.

### D3 — Endpoint en `/usuarios/me/perfil` vs. `/perfil/me`

Mantener el prefijo `/usuarios/` agrupa semánticamente todos los recursos propios del usuario autenticado (`/me/perfil`, `/me/direcciones`). Evita proliferación de prefijos de primer nivel.

### D4 — Validación de campos vacíos en `PerfilUpdate`

Si `nombre` o `apellido` se envían como `""`, se rechaza con 422 usando `field_validator`. Un string vacío no es un nombre válido y no debe sobrescribir datos existentes silenciosamente.

**Regla:** `None` = "no cambiar este campo" (partial update); `""` = error de validación.

### D5 — Usar `get_current_user` (sin UoW en GET)

`GET /me/perfil` no escribe nada. Usará `get_current_user` directamente (que ya tiene su propia sesión). Para `PUT /me/perfil` se necesita `get_uow` porque escribe en BD.

### D6 — Registrar `DireccionEntregaRepository` en `get_uow`

El `PerfilService` necesita filtrar direcciones activas del usuario. Se puede hacer directamente sobre la relación ya cargada en `current_user.direcciones` filtrando por `deleted_at is None` en memoria, sin necesidad de abrir otra consulta. Esto evita acoplamiento del service de usuarios al repositorio de direcciones.

## Risks / Trade-offs

- **[Riesgo] Lazy loading de `direcciones`**: la relación `Usuario.direcciones` puede no estar cargada en la sesión de `get_current_user` (que usa una sesión propia). → **Mitigación:** el endpoint `GET /me/perfil` usará `get_uow` para poder hacer un `select` explícito con `joinedload`, o alternativamente recargar el usuario con sesión del UoW. Decisión final en implementación según comportamiento observado con SQLModel lazy load.
- **[Riesgo] Doble sesión**: `get_current_user` usa una sesión y `get_uow` abre otra. En `PUT /me/perfil` usar únicamente `get_uow` y reconsultar el usuario desde allí. → **Mitigación:** el router del PUT inyecta `get_current_user` solo para extraer el `id`, luego carga el objeto desde el UoW para operar.
- **[Trade-off] `PerfilRead` embebe direcciones**: aumenta el tamaño de la respuesta. Aceptable para un perfil personal; no es una lista paginada de recursos.

## Migration Plan

1. No hay cambios de esquema de BD — `telefono`, `apellido`, `nombre` ya existen en `usuario`.
2. Agregar `PerfilRead` y `PerfilUpdate` en `backend/usuarios/schemas.py`.
3. Agregar `get_perfil` y `update_perfil` en `backend/usuarios/service.py`.
4. Agregar los dos endpoints en `backend/usuarios/router.py`.
5. No se requiere rollback especial — los endpoints nuevos no tocan datos existentes. Si se elimina un endpoint, las rutas simplemente dejan de existir.

## Open Questions

- ¿`GET /me/perfil` debe exponer `apellido` por separado o concatenado como `nombre_completo`? → Preferencia: campos separados para facilitar edición granular en frontend.
- ¿Incluir `updated_at` en `PerfilRead` para que el frontend pueda cachear correctamente? → Sí, se incluye como campo informativo.
