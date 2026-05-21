## Context

La app ya tiene guards de routing (`ProtectedRoute`, `PublicOnlyRoute`) y rutas públicas de autenticación (`/login`, `/register`). Sin embargo, el spec vigente de `frontend-route-guards` asume que la ruta raíz `/` está cubierta por `ProtectedRoute` (por ejemplo: se lista `/` como ruta privada y se incluye un escenario donde `ProtectedRoute` envuelve `/` y sus hijos).

Este change redefine el entrypoint: `/` pasa a ser público y funciona como Home (landing) con un CTA hacia el catálogo público. En paralelo, se mantienen rutas privadas bajo guards para `/perfil`, `/pedidos`, `/checkout` y `/admin/*`.

Restricciones explícitas:
- No se introduce un nuevo destino tipo `/dashboard`.
- `PublicOnlyRoute` sigue redirigiendo a `/`.
- El catálogo permanece público.

## Goals / Non-Goals

**Goals:**
- Hacer que `GET /` en el frontend renderice HomePage sin autenticación.
- Mantener públicas las rutas del catálogo en el branch público.
- Mantener protegidas `/perfil`, `/pedidos`, `/checkout`, `/admin/*` bajo `ProtectedRoute`.
- Ajustar la definición/spec de `frontend-route-guards` para reflejar que `ProtectedRoute` ya no cubre el index `/`.
- Asegurar que un usuario no autenticado que intenta acceder a rutas privadas sea redirigido a `/login`.

**Non-Goals:**
- Rediseño visual completo de HomePage.
- Cambios en backend o en políticas de autenticación.
- Cambiar el comportamiento de `PublicOnlyRoute` o el destino de redirect.

## Decisions

### D1: Dos branches sibling en `path: "/"` (público y protegido)

**Decisión:** Definir dos rutas raíz con el mismo `path: "/"` como siblings:
- Branch público: `Layout` + `index: HomePage` y children públicos (incluyendo catálogo).
- Branch protegido: `ProtectedRoute` sin `index` y solo children privados (`perfil`, `pedidos`, `checkout`, `admin/*`).

**Alternativas consideradas:**
- Envolver todo `/` con `ProtectedRoute` y crear un `/home` público: descartado porque el goal es que `/` sea Home pública.
- Hacer `ProtectedRoute` condicional dentro de `HomePage`: descartado porque mezcla concerns y hace menos explícito qué rutas son privadas.

**Razón:** Mantiene claro el contrato: `/` resuelve siempre a Home pública, mientras que rutas privadas son children explícitos del branch protegido.

### D2: CTA explícito a `/catalogo`

**Decisión:** Asegurar que el Home incluya un CTA navegable a `/catalogo`.

**Alternativas consideradas:**
- Mantener Home minimal sin CTA: descartado porque el objetivo principal del change es mejorar el onboarding hacia el catálogo.

## Risks / Trade-offs

- **Ambigüedad de matching con dos rutas `path: "/"`** → Mitigación: el branch protegido NO define `index`; solo children específicos. El index (`/`) vive solo en el branch público.
- **Links a rutas privadas desde el branch público** → Mitigación: confiar en `ProtectedRoute` para redirigir a `/login`; además, evitar/ocultar links privados en Home cuando no hay sesión (si aplica).
- **Regresión de comportamiento previamente asumido por spec** → Mitigación: delta explícita en `frontend-route-guards` removiendo `/` como ejemplo privado y ajustando el escenario sobre cubrir la raíz.

## Migration Plan

1. Actualizar specs (nuevo `frontend-public-home` + delta de `frontend-route-guards`).
2. Implementar el cambio en `frontend/src/app/router.tsx` según el routing structure decidido.
3. Ajustar Home y/o navegación para CTA hacia `/catalogo`.
4. Smoke manual: anónimo entra a `/` (no redirect), navega a `/catalogo` (ok), intenta `/perfil` (redirect a `/login`), autenticado accede a rutas privadas.

Rollback: revertir cambios de routing y home; no hay migraciones ni estado persistente.

## Open Questions

- Confirmar cuáles son exactamente las rutas del catálogo hoy (ej. `/catalogo` vs `/catalogo/:id` vs `/productos`) para listarlas explícitamente en el router branch público.
