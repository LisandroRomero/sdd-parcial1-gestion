## Why

Hoy el proyecto tiene **inconsistencias** en el formato de error entre documentación y código (p.ej. RFC 7807 vs `{ statusCode, message }` y respuestas actuales con `{ "detail": ... }`). Esto rompe el manejo uniforme de errores en el frontend, complica el debugging (no hay contrato estable) y obliga a codepaths ad-hoc por endpoint/tipo de error.

## What Changes

- Estandarizar un **contrato único** de error para toda la API basado en **RFC 7807 (Problem Details)** como canónico, con extensiones controladas.
- Unificar errores de:
  - excepciones de negocio (`AppException`)
  - validaciones de FastAPI/Pydantic (422)
  - errores no manejados (500)
- Incluir `X-Request-ID` en la respuesta y exponerlo también dentro del body de error para trazabilidad.
- Actualizar el frontend para interpretar el nuevo formato canónico (priorizando `detail` y soportando extensiones como `errors`).
- Alinear documentación del repo (Integrador/README) para que describa el formato real y estable.

## Capabilities

### New Capabilities
- `api-problem-details`: Contrato de error canónico RFC 7807 para todas las respuestas 4xx/5xx, incluyendo shape y extensiones (p.ej. `code`, `errors`, `requestId`, `timestamp`).

### Modified Capabilities
- `core-middleware`: Cambia el formato de serialización de errores a RFC 7807 (manteniendo `X-Request-ID`).
- `core-exceptions`: Extiende/ajusta `AppException` para soportar un `code` estable y datos opcionales de validación/campo.
- `frontend-http-error-handling`: Actualiza el helper de parseo para soportar RFC 7807 canónico y fallbacks.

## Impact

- **Backend**: `backend/core/middleware.py`, `backend/core/exceptions.py` y potencialmente routers/servicios que hoy dependen de `{detail: ...}` o de formatos documentados distintos.
- **Frontend**: manejo global de errores (Axios/TanStack Query) y mensajes mostrados al usuario.
- **Docs**: `docs/Integrador.txt` y `backend/README.md` deben converger al contrato canónico (evitar ejemplos contradictorios).
