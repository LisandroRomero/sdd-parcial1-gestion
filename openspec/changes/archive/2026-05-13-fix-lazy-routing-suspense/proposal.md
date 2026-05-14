## Why

Todas las páginas del frontend usan `React.lazy()` para code-splitting, pero el `<Suspense>` boundary necesario para manejar la suspensión de estos componentes nunca se conectó al árbol de renders. Esto causa que cada navegación entre páginas lance el error de React: *"A component suspended while responding to synchronous input"*, reemplazando la UI con un indicator de carga y rompiendo la experiencia de usuario.

## What Changes

- Usar el componente `RouterLoader` (ya existe en `router.tsx`, envuelve `<RouterProvider>` en un `<Suspense>`) en `providers.tsx` en lugar de usar `RouterProvider` directamente
- Esto conecta el `<Suspense fallback={<LoadingSpinner />}>` existente al árbol de renders, permitiendo que React maneje correctamente la suspensión de los lazy components durante la navegación

## Capabilities

### New Capabilities
- `frontend-app-shell`: Configuración del shell de la aplicación (providers, router, suspense boundary). Garantiza que toda navegación entre páginas lazy-loaded esté envuelta en un Suspense boundary funcional.

### Modified Capabilities
<!-- No se modifican specs existentes — es un fix puramente de infraestructura del frontend, no cambia requerimientos de ninguna capability existente -->

## Impact

- `frontend/src/app/providers.tsx` — Cambiar import de `{ router }` a `{ RouterLoader }` y reemplazar `<RouterProvider router={router} />` por `<RouterLoader />`
- `frontend/src/app/router.tsx` — No requiere cambios (RouterLoader ya existe y está correctamente implementado)
