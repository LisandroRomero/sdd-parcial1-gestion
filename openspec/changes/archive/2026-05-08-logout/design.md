## Context

Los Epics 1.1–1.3 implementaron registro, login y refresh de tokens. El ciclo completo de sesión exige también una forma explícita de invalidarla. La tabla `refreshtoken` ya tiene la columna `revoked_at`; el repository ya expone `revoke(id)` y `get_by_hash(hash)`. No hay migración pendiente.

## Goals / Non-Goals

**Goals:**
- Exponer `POST /api/v1/auth/logout` que revoca el refresh token activo del usuario.
- Requerir autenticación (access token) para identificar al solicitante.
- Devolver 204 No Content en éxito, 400 para token inválido/ya-revocado, 401 para acceso no autenticado.

**Non-Goals:**
- Blacklist de access tokens (quedan válidos hasta su expiración de 30 min — aceptado por diseño).
- Logout "global" (revocar todos los tokens del usuario a la vez — eso ya lo hace el replay-attack de 1.3).
- Implementación frontend.

## Decisions

### 1. El endpoint exige Bearer access token

El `get_current_user` DI ya implementado verifica la firma JWT y devuelve el `Usuario`. Usarlo garantiza que solo el dueño puede revocar su token y desacopla la lógica de autenticación del servicio de logout.

Alternativa descartada: aceptar solo el `refresh_token` sin access token. Descartada porque cualquiera con el refresh token podría invalidar la sesión de otro usuario.

### 2. Verificar que el refresh token pertenece al usuario autenticado

Tras hallar el token en BD, comparar `stored.usuario_id == current_user.id`. Si no coincide → 400. Esto previene que un token robado de otro usuario sea revocado silenciosamente sin su conocimiento.

### 3. 400 Bad Request para refresh token inválido/revocado (no 401)

401 indica que el cliente no está autenticado para acceder al recurso. En logout, el cliente ya se autenticó con el access token; el refresh token incorrecto es un error del body (datos inválidos), no de identidad. Semánticamente es 400.

### 4. No agregar método nuevo al repository — componer los existentes

`get_by_hash` + `revoke(id)` es suficiente. Agregar un método `revoke_by_hash` sería YAGNI: la única lógica adicional (verificar ownership y revocation state) pertenece al service, no al repo.

### 5. Agregar `BadRequestException` a `core/exceptions.py`

`ConflictException`, `UnauthorizedException`, etc. siguen el patrón de excepciones semánticas del proyecto. Lanzar `HTTPException(400)` directamente desde el service rompe la separación de capas. Se agrega `BadRequestException(status_code=400)` para completar el conjunto.

## Risks / Trade-offs

- **Access token sigue válido 30 min post-logout** → Mitigación: expiración corta de 30 min. Aceptable en el contexto del proyecto.
- **Usuario puede perder el refresh token (ej. browser cerrado)** → El token expira en 7 días de todas formas; no es un riesgo de seguridad.

## Migration Plan

1. Agregar `BadRequestException` a `backend/core/exceptions.py`.
2. Agregar schema `LogoutRequest` a `backend/auth/schemas.py`.
3. Implementar `logout(uow, body, current_user)` en `backend/auth/service.py`.
4. Agregar endpoint `POST /logout` en `backend/auth/router.py`.
5. Sin migraciones Alembic — la tabla `refreshtoken` ya tiene `revoked_at`.
