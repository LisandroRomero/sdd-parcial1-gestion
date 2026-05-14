## Context

El frontend usa `React.lazy()` para code-splitting de todas las páginas (8 rutas lazy). React.lazy() requiere un `<Suspense>` boundary ancestro para manejar la suspensión mientras se carga el chunk. `router.tsx` ya define un componente `RouterLoader` que envuelve `<RouterProvider>` en `<Suspense>` con un fallback visual (`<LoadingSpinner>` centrado), pero `providers.tsx` nunca lo importa — en su lugar usa `RouterProvider` directamente.

Esto causa que cada navegación entre páginas (click en link, submit de formulario, etc.) dispare el error de React 18: *"A component suspended while responding to synchronous input"*, porque React no encuentra un `<Suspense>` en el árbol hacia arriba desde el lazy component.

## Goals / Non-Goals

**Goals:**
- Eliminar el error de Suspense en toda navegación entre páginas
- Usar el componente `RouterLoader` ya existente en `router.tsx`
- Mantener el fallback visual existente con `LoadingSpinner`

**Non-Goals:**
- Refactorizar la estructura de routing o lazy loading
- Agregar `startTransition` a navegaciones individuales (la solución correcta es tener el Suspense boundary)
- Modificar `router.tsx` (el componente ya existe y es correcto)
- Agregar ErrorBoundary específico para Suspense (no es necesario con el Suspense en el nivel correcto)

## Decisions

### D1: Usar RouterLoader existente vs agregar Suspense inline

Se decidió usar `RouterLoader` porque ya existe y está correctamente implementado con:
- `<Suspense>` con `fallback` tipado
- `<LoadingSpinner>` centrado en pantalla (`flex items-center justify-center min-h-screen`)
- Misma semántica que `RouterProvider` pero con el Suspense wrapper

Alternativa descartada: Agregar `<Suspense>` inline en `providers.tsx`. Funcionalmente sería equivalente, pero `RouterLoader` ya está definido, es más limpio y evita duplicación.

### D2: Un solo Suspense boundary a nivel providers

Se envuelve todo el `RouterProvider` en un solo `<Suspense>` a nivel de providers — no uno por ruta. Esto es correcto porque:
- React Router maneja la desmontura/montaje de páginas internamente
- Un solo boundary arriba captura todas las suspensiones de todos los lazy components
- Es el patrón recomendado por React Router para lazy-loaded routes

### D3: No requiere startTransition en navegaciones

El error sugiere usar `startTransition`, pero la causa raíz real es la falta de `<Suspense>`. Agregar `startTransition` enmascararía el síntoma sin resolver la causa. Con el `<Suspense>` en su lugar, React maneja correctamente la transición.

## Risks / Trade-offs

- **[Bajo]** El fallback del Suspense (`<LoadingSpinner>`) se muestra brevemente en cada navegación si el chunk tarda en cargarse. Esto es deseable — es mejor que el error actual. Si los chunks son pequeños, la pantalla ni siquiera alcanza a mostrar el spinner.
- **[Bajo]** Si en el futuro se agregan componentes lazy fuera del árbol del router (ej. modales lazy), necesitarán su propio Suspense boundary. Esto es independiente de este cambio.
