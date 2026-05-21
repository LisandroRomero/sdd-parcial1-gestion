## Why

Hoy la ruta `/` (Home) queda detrás del guard de autenticación por cómo está integrado `ProtectedRoute` en el router. Eso degrada el onboarding: un usuario anónimo aterriza en la app y es redirigido a `/login` incluso cuando solo quiere explorar el catálogo.

## What Changes

- Hacer que `/` (HomePage) sea pública y accesible sin autenticación.
- Mantener públicas las rutas del catálogo (ej. `/catalogo` y sus subrutas).
- Mantener privadas las rutas `/perfil`, `/pedidos`, `/checkout` y `/admin/*`.
- Ajustar la estructura del router para que exista un branch público con `Layout` en `path: "/"` e `index: HomePage`, y un branch protegido sibling en `path: "/"` sin `index`, solo con children privados (`perfil`, `pedidos`, `checkout`, `admin/*`).
- Mantener `PublicOnlyRoute` con redirect target `/` (no se introduce `/dashboard`).

## Capabilities

### New Capabilities

- `frontend-public-home`: La ruta `/` es pública y el Home provee un CTA hacia `/catalogo`; intentos de acceder a rutas privadas desde estado no autenticado redirigen a `/login`.

### Modified Capabilities

- `frontend-route-guards`: Se actualiza la definición de qué rutas quedan cubiertas por `ProtectedRoute` (ya no cubre el index `/`) y se ajustan los ejemplos/escenarios que asumen que `/` es una ruta privada.

## Impact

- **Frontend routing**: cambios en `frontend/src/app/router.tsx` para separar branch público vs branch protegido en la raíz.
- **Home / navegación**: posible ajuste en HomePage y/o navegación para incluir CTA claro a `/catalogo` y evitar links privados sin guard.
- **Sin cambios en backend**.
- **Sin nuevas dependencias**.
