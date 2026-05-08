## Context

El endpoint `POST /api/v1/auth/login` (Epic 1.2) ya emite un par de tokens: access token (30 min) + refresh token (7 días). El refresh token se almacena en BD como SHA-256 hash en la tabla `refreshtoken` con campo `revoked_at` nullable. El `RefreshTokenRepository` tiene `create()` y `get_by_hash()` implementados.

El access token dura 30 minutos. Sin rotación, el frontend debe redirigir al login cada vez que expira — experiencia inaceptable para una app de órdenes de comida donde el usuario está en medio de un pedido.

Contexto de seguridad clave: el modelo `RefreshToken` ya tiene el campo `revoked_at` (diseñado específicamente para soportar revocación). La rotación es la práctica estándar para evitar que un refresh token robado sea válido indefinidamente.

## Goals / Non-Goals

**Goals:**

- Implementar `POST /api/v1/auth/refresh` que acepta un refresh token en el body y retorna un nuevo par de tokens (access + refresh).
- Aplicar token rotation: al usar un refresh token, se revoca el anterior y se emite uno nuevo.
- Detectar replay attacks: si un refresh token ya revocado es presentado, revocar TODOS los tokens activos del usuario (token family invalidation) y retornar HTTP 401.
- Agregar `revoke(token_id)` y `revoke_all_for_user(usuario_id)` al `RefreshTokenRepository`.
- Rate limiting 10 requests / 15 minutos por IP.

**Non-Goals:**

- Logout explícito (POST /auth/logout) → Epic 1.4.
- Refresh token en cookie httpOnly → el scope del parcial usa body JSON (consistente con el login).
- Frontend interceptor Axios que llama automáticamente a este endpoint → Epic 1.6.
- Verificación de token expirado mediante endpoint independiente.

## Decisions

### 1. Refresh token viaja en el body JSON (no en header Authorization)

**Decisión**: `POST /api/v1/auth/refresh` recibe `{ refresh_token: str }` en el body.

**Rationale**: Consistente con el diseño del login (ver `archive/2026-05-08-user-login-with-jwt/design.md`). El spec técnico SDD v5.0 define explícitamente `POST /api/v1/auth/refresh` con `{ refresh_token }` en el body. Mantener consistencia evita confusión en el cliente.

**Alternativa descartada — Header `Authorization: Bearer <refresh_token>`**: Podría parecer más "RESTful" pero mezcla semántica: `Authorization` se usa para access tokens en el resto de la API. Usar el mismo header para ambos tipos de token crea ambigüedad en el middleware de autenticación.

**Alternativa descartada — Cookie httpOnly**: Mayor seguridad contra XSS pero requiere configuración de CORS adicional, manejo de SameSite, y cambia el contrato con el frontend. Fuera de scope del parcial.

### 2. Token family invalidation al detectar replay

**Decisión**: Si `get_by_hash(hash)` retorna un registro con `revoked_at IS NOT NULL`, se llama a `revoke_all_for_user(usuario_id)` del token encontrado y se retorna HTTP 401.

**Rationale**: Un refresh token revocado siendo presentado indica compromiso de sesión (el token fue robado y usado por un atacante DESPUÉS de que el usuario legítimo ya lo rotó). La respuesta correcta es invalidar toda la familia — si el atacante tiene el token antiguo, puede tener tokens rotados también. Esta es la recomendación estándar de OAuth 2.0 (RFC 6749 + Security BCP).

**Trade-off**: El usuario legítimo también pierde su sesión. Pero la alternativa (no invalidar) permite al atacante continuar usando tokens rotados indefinidamente. En un sistema de pedidos de comida con pagos, el riesgo de no invalidar supera la molestia del re-login.

### 3. Validación de refresh token: firma JWT primero, luego BD

**Decisión**: El flujo de validación es (1) `verify_token(token)` para verificar firma y expiración JWT, (2) luego `get_by_hash(sha256(token))` para verificar existencia y estado en BD.

**Rationale**: Falla rápido sin hit a BD si el token está malformado o expirado. La firma JWT es stateless y barata computacionalmente. La BD solo se consulta si el token es criptográficamente válido.

**Importante**: `verify_token()` actual en `security.py` NO distingue entre tokens de tipo `access` y `refresh` — solo verifica firma y expiración. En el service de refresh se debe verificar que el claim `"type"` sea `"refresh"` para evitar que un access token sea usado como refresh token.

### 4. revoke_all_for_user usa UPDATE masivo, no SELECT + loop

**Decisión**: `revoke_all_for_user(usuario_id)` ejecuta un `UPDATE refreshtoken SET revoked_at = now() WHERE usuario_id = :id AND revoked_at IS NULL` en una sola query.

**Rationale**: Eficiencia. Un usuario puede tener múltiples sesiones activas (varios dispositivos). El UPDATE masivo evita N+1 queries. SQLModel/SQLAlchemy soporta `update()` con `where()` directamente.

### 5. El service de refresh NO usa get_current_user dependency

**Decisión**: `POST /api/v1/auth/refresh` no requiere `Authorization: Bearer` header — el refresh token en el body ES la credencial. No se inyecta `get_current_user`.

**Rationale**: El endpoint está diseñado precisamente para cuando el access token expiró. Requerir un access token válido para obtener uno nuevo sería contradictorio.

### 6. Rate limiting: 10 requests / 15 minutos (más permisivo que login)

**Decisión**: `@limiter.limit("10/15minutes")` — el doble del límite de login.

**Rationale**: El refresh es invocado automáticamente por el interceptor Axios (transparente al usuario), no por acción explícita. Un límite muy restrictivo causaría falsos positivos en usuarios legítimos con muchas pestañas abiertas. 10 requests en 15 min es suficiente para detectar abuso sin penalizar uso normal.

## Risks / Trade-offs

- **[Risk] verify_token no valida claim `type`** → Si se pasa un access token al endpoint de refresh, `verify_token` lo acepta. Mitigación: en el service, verificar explícitamente `payload.get("type") == "refresh"` y lanzar `UnauthorizedException` si no coincide.

- **[Risk] Race condition en token rotation** → Dos requests concurrentes con el mismo refresh token podrían ambos pasar la validación antes de que el primero revoque. Mitigación: la constraint `UNIQUE` en `token_hash` más la transacción UoW garantizan que solo uno puede crear el nuevo token. El segundo request fallará en el `get_by_hash` (token ya revocado) y recibirá 401. Riesgo aceptable para el scope del parcial.

- **[Trade-off] El usuario legítimo pierde sesión en replay detection** → Al detectar replay, todos los tokens del usuario se invalidan, forzando re-login. Es el comportamiento correcto por seguridad pero puede sorprender al usuario. El mensaje de error debe ser claro: "Sesión invalidada por seguridad. Por favor inicie sesión nuevamente."

- **[Risk] refresh_token expirado en BD pero no en JWT** → Imposible — la expiración JWT y la expiración en BD se calculan con el mismo `REFRESH_TOKEN_EXPIRE_DAYS`. La validación JWT falla primero si el token expiró.

## Migration Plan

Sin cambios de esquema de BD. El campo `revoked_at` ya existe en la tabla `refreshtoken` desde la migración del change `database-schema-and-seed`.

Pasos de deploy:
1. Agregar `revoke()` y `revoke_all_for_user()` a `RefreshTokenRepository`.
2. Agregar schema `RefreshRequest` en `backend/auth/schemas.py`.
3. Implementar función `refresh_tokens()` en `backend/auth/service.py`.
4. Agregar endpoint `POST /refresh` en `backend/auth/router.py`.

Rollback: revertir los archivos Python. No hay cambio de BD.

## Open Questions

Ninguna. Todas las decisiones de diseño están resueltas con la información disponible del contexto técnico y del spec SDD v5.0.
