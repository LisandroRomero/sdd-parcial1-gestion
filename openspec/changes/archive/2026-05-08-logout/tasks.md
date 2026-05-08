## 1. Infraestructura core

- [x] 1.1 Agregar `BadRequestException` a `backend/core/exceptions.py` (status_code=400, mensaje por defecto "Solicitud inválida")

## 2. Schemas

- [x] 2.1 Agregar `LogoutRequest` a `backend/auth/schemas.py` con campo `refresh_token: str`

## 3. Service

- [x] 3.1 Implementar función `logout(uow, body, current_user)` en `backend/auth/service.py`:
  - SHA-256 hash del `body.refresh_token`
  - Buscar en BD con `uow.repos.refresh_tokens.get_by_hash(token_hash)`
  - Si no existe → lanzar `BadRequestException("Refresh token inválido")`
  - Si `stored.revoked_at is not None` → lanzar `BadRequestException("Refresh token ya revocado")`
  - Si `stored.usuario_id != current_user.id` → lanzar `BadRequestException("Refresh token inválido")`
  - Llamar `uow.repos.refresh_tokens.revoke(stored.id)`

## 4. Router

- [x] 4.1 Agregar endpoint `POST /logout` en `backend/auth/router.py`:
  - `response_model=None`, `status_code=204`
  - Depende de `get_current_user` (Bearer access token) y `get_uow`
  - Llama a `logout(uow, body, current_user)` y luego `uow.commit()`
  - Retorna `Response(status_code=204)`

## 5. Verificación

- [x] 5.1 Levantar el servidor y verificar logout exitoso → 204
- [x] 5.2 Verificar que el refresh token queda con `revoked_at` en BD
- [x] 5.3 Verificar que un segundo intento de logout con el mismo token → 400
- [x] 5.4 Verificar llamada sin Authorization header → 401
- [x] 5.5 Verificar que el refresh token revocado ya no puede hacer refresh → 401 desde /refresh
