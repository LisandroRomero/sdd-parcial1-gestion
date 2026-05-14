## Context

Hoy el backend devuelve errores en un formato inconsistente: `{"detail": "mensaje"}` para `AppException`, `{"detail": [...]}` para errores de validación Pydantic, y el manejador por defecto de FastAPI para `RequestValidationError` (que devuelve otro formato). El frontend intenta parsear `detail` en `getErrorMessage()` pero no hay garantía de forma estable.

La documentación (Integrador.txt) describe un formato RFC 7807 que no coincide con la implementación actual, generando confusión.

**Problemas identificados:**
1. Sin contrato de error canónico entre backend y frontend
2. Códigos HTTP 409, 422 y 401 no tienen mensajes en el frontend
3. El `X-Request-ID` está en headers pero no en el body de error, imposibilitando trazabilidad en logs del frontend
4. Handler de `ValidationError` de Pydantic duplicado entre middleware y register_exception_handlers
5. No hay sanitización de inputs (XSS/SQLi) a nivel middleware

## Goals / Non-Goals

**Goals:**
- Implementar **RFC 7807 (Problem Details)** como formato canónico único para toda respuesta 4xx/5xx
- Unificar todos los exception handlers bajo el mismo formato
- Incluir `X-Request-ID` en el body de error (`requestId`) para trazabilidad
- Extender la jerarquía `AppException` con un campo `code` (código interno estable) y `errors` (para errores de validación por campo)
- Actualizar el frontend (`getErrorMessage`) para interpretar RFC 7807 canónico, agregando soporte para 409, 422 y 401
- Agregar sanitización de inputs (XSS básico en strings, SQLi prevention en filtros de búsqueda)
- Alinear `docs/Integrador.txt` con el formato real

**Non-Goals:**
- NO cambiar los códigos HTTP existentes de cada excepción
- NO reescribir routers/services que ya funcionan
- NO implementar un sistema de logging centralizado (eso es otro change)
- NO cambiar el interceptor de refresh token del frontend (funciona bien)
- NO implementar notificaciones toast/snackbar globales (eso es 8.3)

## Decisions

### Decision 1: RFC 7807 como formato canónico

**Contexto:** Hoy hay 3 formatos distintos: `{"detail": str}` para AppException, `{"detail": [...]}` para ValidationError de Pydantic, y el formato default de FastAPI para RequestValidationError.

**Decisión:** Adoptar **RFC 7807 Problem Details** (`application/problem+json`) como el formato único.

**Shape canónico:**
```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Recurso no encontrado",
  "instance": "/api/v1/productos/999",
  "requestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-05-14T12:00:00Z"
}
```

**Extensiones controladas:**
- `code` (string, opcional): Código interno estable como `"PRODUCT_NOT_FOUND"` para identificación programática
- `errors` (array, opcional): Errores de validación por campo, cada uno con `{ "field": "email", "message": "Email inválido", "code": "invalid_email" }`

**Alternativa considerada:** Mantener `{"detail": ...}` y agregar campos. Descartado porque no hay un contrato formal para extensiones, no hay campo `status` en el body, y el frontend no puede determinar el tipo de error sin parsear el status code HTTP.

### Decision 2: Mapeo de excepciones a RFC 7807 vía middleware unificado

**Contexto:** Hoy hay 4 handlers separados registrados con `@app.exception_handler`.

**Decisión:** Reemplazar los 4 handlers por **uno solo** que reciba `Exception` genérico, detecte el tipo, construya el RFC 7807 y lo serialice. Esto elimina la duplicación de `ValidationError` y centraliza la lógica.

**Flujo:**
1. Un solo `global_exception_handler(request, exc: Exception)` en `register_exception_handlers`
2. Dentro: `match type(exc)` → `AppException` | `RequestValidationError` | `ValidationError` | `Exception`
3. Cada branch construye un `ProblemDetail` dataclass/dict con los campos de RFC 7807
4. Serializa a JSON con `media_type="application/problem+json"`

### Decision 3: Campo `code` en AppException

**Contexto:** Hoy las excepciones solo tienen `status_code` y `detail`. No hay forma de identificar programáticamente el tipo de error en el frontend sin parsear strings.

**Decisión:** Agregar `code: str` opcional a `AppException` con un identificador estable estilo `"PRODUCT_NOT_FOUND"`, `"INVALID_EMAIL"`, `"UNAUTHORIZED"`.

```python
class AppException(Exception):
    def __init__(self, status_code: int, detail: str, code: str | None = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.code = code
```

Las subclases existentes se actualizan para pasar su `code` por defecto:
- `NotFoundException` → `"RESOURCE_NOT_FOUND"`
- `ConflictException` → `"CONFLICT"`
- `UnauthorizedException` → `"UNAUTHORIZED"`
- `ForbiddenException` → `"FORBIDDEN"`
- `ValidationException` → `"VALIDATION_ERROR"`
- `BadRequestException` → `"BAD_REQUEST"`

### Decision 4: Errores de validación como array de `errors`

**Contexto:** Hoy `ValidationError` de Pydantic devuelve `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` que es el formato interno de Pydantic.

**Decisión:** Transformar los errores de validación a un formato `errors` canónico dentro del RFC 7807:
```json
{
  "type": "about:blank",
  "title": "Validation Error",
  "status": 422,
  "detail": "Error de validación en los datos enviados",
  "errors": [
    { "field": "email", "message": "El email no es válido", "code": "invalid_email" },
    { "field": "password", "message": "La contraseña debe tener al menos 8 caracteres", "code": "too_short" }
  ]
}
```

### Decision 5: `X-Request-ID` en body del error

**Contexto:** Hoy el `X-Request-ID` viaja solo en headers. Cuando el frontend logea un error, pierde el request ID porque el header no está accesible desde `getErrorMessage`.

**Decisión:** El middleware de request ID pasa el `request_id` a `request.state.request_id`, y el exception handler lo lee de ahí para incluirlo en el body como `requestId`.

### Decision 6: Sanitización de inputs vía middleware

**Contexto:** El proyecto no tiene sanitización a nivel entrada.

**Decisión:** Agregar un middleware `InputSanitizationMiddleware` (opcional, desactivado por defecto, configurable vía setting) que:
- Stripea tags HTML básicos de campos string en request bodies (XSS básico)
- Detecta patrones SQLi conocidos en query params y bodies de búsqueda y rechaza con 400
- No afecta campos binarios ni datos estructurados como JSON anidado

### Decision 7: Frontend — actualizar `getErrorMessage` a RFC 7807

**Contexto:** Hoy el helper parsea solo `detail`.

**Decisión:** Actualizar `getErrorMessage` para:
1. Intentar `errors[0].message` si hay errores de validación
2. Fallback a `detail`
3. Fallback a mensaje por código HTTP
4. Agregar mensajes para 409 ("Conflicto con el estado actual del recurso"), 422 ("Error de validación"), 401 ("Sesión expirada. Iniciá sesión de nuevo.")

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Breaking change**: Frontends existentes esperan `{"detail": ...}` y se rompen con el nuevo formato | El `detail` se mantiene en RFC 7807. `getErrorMessage` se actualiza primero (commit previo al backend). Período de solapamiento: frontend tolera ambos formatos. |
| **Pérdida de info de Pydantic**: Los errores de Pydantic tienen info de `loc` (ubicación del error) que se perdería con `field` simplificado | Mapear `loc[1:]` a dotted path: `["body", "user", "email"]` → `"user.email"`. El detail incluye el msg original. |
| **Performance**: Middleware de sanitización agrega latencia | Se limita a strings cortos (<10KB). Se puede desactivar por endpoint o desactivar completamente si impacta. |
| **Duplicación temporal**: El handler viejo y nuevo coexisten durante el cambio | Se hace un solo commit que reemplaza TODO el manejador. No hay migración gradual. |
| **`application/problem+json`**: Algunos proxies/CDN pueden no manejar este media type | Se usa `JSONResponse` con media type explícito. Si hay problemas, se cae a `application/json`. |

## Migration Plan

**Fase 1 — Frontend tolerance (previo al cambio de backend):**
1. Actualizar `getErrorMessage` para parsear RFC 7807 (`title`, `detail`, `errors`, `requestId`)
2. Mantener compatibilidad con formato legacy (`{"detail": ...}`)
3. Deployar

**Fase 2 — Backend (un commit atómico):**
1. Agregar `code` a `AppException` y subclases
2. Reemplazar `register_exception_handlers` por un handler unificado RFC 7807
3. Incluir `request.state.request_id` en el body
4. Agregar `InputSanitizationMiddleware` (configurable)
5. Registrar `RequestIDMiddleware` y el handler en orden correcto
6. Deployar

**Fase 3 — Frontend canónico (post-backend):**
1. Quitar compatibilidad con formato legacy
2. Actualizar specs de frontend para reflejar formato canónico

**Rollback:** Volver al commit anterior del backend. El frontend mantiene doble formato, asi que rollback del backend solo no rompe el frontend.

## Open Questions

1. ¿El `InputSanitizationMiddleware` debería estar activado por defecto o requerir configuración explícita? → Decisión: off por defecto, se activa con `SANITIZE_INPUTS=true`
2. ¿Debemos usar `about:blank` como `type` o apuntar a una URL de documentación? → Usar `about:blank` por ahora; en el futuro se puede apuntar a `/docs/errors/{code}`
3. ¿Los errores 500 no controlados deberían incluir `requestId` en producción? → Sí, siempre. Para debugging expuesto controlado.
