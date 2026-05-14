## Context

El módulo `backend/admin/` existe con archivos vacíos y no está registrado en el router de la API. El frontend no tiene páginas ni rutas admin. El campo `activo: bool` existe en el modelo `Usuario` pero el login nunca lo evalúa — usuarios desactivados pueden autenticarse sin restricción.

Los endpoints de gestión de roles (`PUT /api/v1/usuarios/{id}/roles`) ya existen en `backend/usuarios/` con la lógica RN-RB04 (último ADMIN no puede degradarse). Esta lógica NO se duplica — el service de admin la reimplementa de forma autónoma.

## Goals / Non-Goals

**Goals:**
- Implementar módulo admin completo para gestión de usuarios (US-053..US-055)
- Bloquear login de usuarios inactivos con 403 (US-055)
- Panel frontend de usuarios admin con tabla, búsqueda, filtro y acciones inline

**Non-Goals:**
- Gestión de pedidos desde admin (7.4)
- Dashboard de métricas (7.1)
- Gestión de catálogo desde admin (7.3)
- Hard delete de usuarios

## Decisions

### D1: activo=False → 403, no 401

**Decisión:** Retornar `ForbiddenException(403, "Cuenta desactivada")` después de la validación de password, como check separado.

**Alternativa descartada:** Unificar con el 401 de credenciales inválidas (mismo mensaje). Descartado porque la spec (US-055) requiere explícitamente 403 para cuentas desactivadas, y el usuario ya demostró que sus credenciales son correctas.

**Trade-off aceptado:** Revela que la cuenta existe. Aceptado — el spec lo requiere y la seguridad por oscuridad no aplica aquí.

### D2: Admin endpoints en `backend/admin/` separado de `backend/usuarios/`

**Decisión:** Todo el CRUD admin de usuarios vive en `backend/admin/` — schemas, repository, service, router propios.

**Alternativa descartada:** Agregar endpoints en `backend/usuarios/router.py` con guard ADMIN. Descartado — mezclaría concerns (usuario ve sus propios datos vs admin ve todos) y contaminaría el módulo de usuarios con lógica administrativa.

**Consecuencia:** El admin repository hace `SELECT` sobre la tabla `usuarios` independientemente del repository de usuarios — no hay reutilización directa, lo cual es intencional.

### D3: Invalidación de tokens al desactivar o cambiar rol

**Decisión:** Al desactivar un usuario o cambiar su rol, el service admin revoca TODOS sus refresh tokens activos usando `RefreshTokenRepository.revoke_all_by_user(usuario_id)`.

**Alternativa descartada:** Invalidar tokens via revocación lazy (verificar `activo` en cada uso del refresh token). Descartado — más complejo, inconsistente con el modelo de revocación existente.

**Resultado:** El próximo uso de cualquier refresh token del usuario afectado falla. El usuario debe re-autenticarse para obtener un token con el nuevo rol.

### D4: Frontend — tabla + modal de edición (no página separada)

**Decisión:** `AdminUsuariosPage` es una sola página con tabla de usuarios y un modal de edición de rol. El toggle de estado (activo/inactivo) es una acción inline en la tabla.

**Alternativa descartada:** Página separada `/admin/usuarios/:id/editar`. Descartado — agrega complejidad de routing para un formulario simple con 2-3 campos.

### D5: Búsqueda server-side con `ilike` sobre nombre y email

**Decisión:** El param `buscar` aplica `ilike` sobre `nombre OR email` del usuario. Sin índice full-text — volumen esperado de usuarios es manejable.

### D6: RN-RB04 en admin service

**Decisión:** El service admin reimplementa la lógica "no puede quitar el último ADMIN" localmente, sin llamar al service de usuarios.

**Razón:** Evitar acoplamiento cross-módulo entre admin y usuarios. La lógica es corta (count_by_role + check).

## Risks / Trade-offs

- **[Revocación masiva de tokens]** Al cambiar rol, todos los refresh tokens del usuario se revocan → el usuario es deslogueado de todas las sesiones. Intencional — el nuevo rol debe aplicar en el próximo login.
- **[Sin migración Alembic]** El campo `activo` ya existe en la tabla. No hay cambios de schema.
- **[Admin router no está registrado]** Hay que agregarlo a `backend/api/v1/router.py` — es fácil de olvidar.
