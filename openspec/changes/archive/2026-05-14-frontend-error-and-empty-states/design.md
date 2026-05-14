## Context

El frontend hoy implementa estados (loading/empty/error) de forma heterogenea: algunas pantallas usan `ErrorMessage`/`EmptyState` (shared/ui), otras renderizan mensajes sueltos o skeletons ad-hoc. Existe `getErrorMessage(error)` en `frontend/src/shared/api/errors.ts` con mapeo de errores HTTP y fallback a "sin conexion" cuando no hay `response`.

Este cambio busca estandarizar la UX de estados en TODAS las superficies del frontend (publico, cliente autenticado y admin) sin introducir errores "full-page": los errores deben ser inline y con reintento cuando sea posible.

Restricciones:
- React 18 + TanStack Query: los estados deben mapearse directamente desde `isLoading/isPending`, `isError`, `error` y `refetch`/`mutate`.
- Mantener consistencia con helpers existentes (`getErrorMessage`, `getErrorRequestId`) y componentes ya presentes (`ErrorMessage`, `EmptyState`).

## Goals / Non-Goals

**Goals:**

- Definir un set unico de estados UI: loading, empty, error (inline), offline, no-permission.
- Proveer componentes compartidos ubicados en `frontend/src/shared/ui` (o subcarpetas) con API estable para reutilizacion.
- Definir reglas de mapeo para:
  - Mensajes de error (usar `getErrorMessage` y, si aplica, `getErrorRequestId`).
  - Estados de TanStack Query (cuando bloquear vs cuando mostrar datos stale).
  - Deteccion offline.
  - No-permission (401/403, y casos por rol).

**Non-Goals:**

- No se redisenia la navegacion ni se reemplazan route guards existentes.
- No se cambia el contrato de APIs backend ni el formato RFC7807.
- No se define un design system nuevo: se reutilizan estilos y componentes base existentes.

## Decisions

1. Reusar y formalizar componentes existentes antes de crear nuevos.
Rationale: ya hay `ErrorMessage`/`EmptyState` usados en features como direcciones y pedidos; el cambio debe minimizar duplicacion.
Alternativas consideradas:
- Crear un componente unico `PageState` que envuelva todo: se descarta porque empuja a errores full-page y reduce flexibilidad.

2. Errores SIEMPRE inline (no full-page) y con reintento cuando exista accion.
Rationale: para pantallas con contenido parcial (stale data, formularios, listas) el error debe convivir con UI existente.
Implementacion propuesta:
- `ErrorMessage` se usa como bloque inline (dentro de layout), con props `message` y `onRetry?`.
- Para mutations, el error se muestra cercano al CTA/form (ej: debajo del boton), con un boton "Reintentar" cuando la accion sea idempotente o tenga sentido.

3. Mapeo de mensajes de error centralizado en `getErrorMessage`.
Rationale: ya contiene mapeo por status HTTP (401/403/404/422/429/500) y valida mensajes de `errors[0].message` / `detail`.
Decision:
- Todo componente de error debe recibir `error: unknown` o `message: string`, pero el mapeo de `unknown` a texto se hace con `getErrorMessage` (y opcionalmente `getErrorRequestId`).
- No se duplican tablas de mensajes por pantalla.

4. Offline como estado explicito, no solo como mensaje generico.
Rationale: `getErrorMessage` puede devolver "Sin conexion..." pero no captura el estado global de conectividad.
Decision:
- Agregar `useOffline()` (ej: `frontend/src/shared/lib/hooks/useOffline.ts`) basado en `navigator.onLine` y eventos `online/offline`.
- Agregar componente inline `OfflineMessage` (ej: `frontend/src/shared/ui/OfflineMessage`) para mostrar banner/mensaje y deshabilitar reintentos si el navegador esta offline.

5. No-permission mapeado por dos vias: route-level y API-level.
Rationale: existen guards por rol, pero igualmente se pueden recibir 401/403 desde API.
Decision:
- Route guards mantienen el control de acceso y redirecciones.
- En pantallas con queries/mutations, si el error es 401/403 (via `getErrorMessage` + status/shape), se muestra un estado inline `NoPermissionMessage` con CTA (ej: "Iniciar sesion" para 401, "Volver" para 403).

6. Patrones recomendados para TanStack Query.
Decision:
- Queries:
  - `isLoading && !data`: mostrar loading (skeleton o placeholder shared).
  - `isError && !data`: mostrar error inline con `onRetry={refetch}`.
  - `data` presente + `isFetching`: mostrar indicador sutil de refresco (opcional) sin reemplazar contenido.
  - `data` presente + error en refetch: mostrar error inline no bloqueante y conservar datos.
- Empty:
  - Si la coleccion esta vacia y no hay loading, mostrar `EmptyState` con CTA por defecto de la pantalla (ej: catalogo, agregar direccion, etc.).

## Risks / Trade-offs

- [Riesgo] Inconsistencia si algunas pantallas no migran. -> Mitigacion: tareas por pantalla + reemplazo de patrones ad-hoc.
- [Riesgo] Confusion entre offline global y error de red puntual. -> Mitigacion: `useOffline()` para estado global + `getErrorMessage()` para fallback por request.
- [Trade-off] Mantener inline errors puede requerir ajustar layouts existentes. -> Mitigacion: componentes compactos y reutilizables en shared/ui.
