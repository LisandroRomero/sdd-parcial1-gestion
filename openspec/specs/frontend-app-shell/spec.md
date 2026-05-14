### Requirement: App shell SHALL wrap RouterProvider in Suspense boundary

El componente raíz `Providers` SHALL usar `RouterLoader` (que envuelve `<RouterProvider>` en `<Suspense>`) en lugar de `<RouterProvider>` directamente, de modo que toda navegación entre páginas lazy-loaded esté envuelta en un Suspense boundary funcional.

#### Scenario: Navigation between lazy-loaded pages does not throw Suspense error

- **GIVEN** the app is rendered with `RouterLoader` wrapping `RouterProvider` in `<Suspense>`
- **WHEN** the user navigates to any page (click a link, submit a form, programmatic `navigate()`)
- **THEN** React SHALL NOT throw *"A component suspended while responding to synchronous input"*
- **THEN** if the lazy chunk is loading, a `<LoadingSpinner>` centered on screen SHALL be displayed as fallback

#### Scenario: RouterLoader is imported and used instead of raw RouterProvider

- **GIVEN** `providers.tsx` imports from `./router`
- **WHEN** the app renders
- **THEN** `RouterLoader` SHALL be the imported component used, not `router` directly
- **THEN** `<RouterLoader />` SHALL appear in the JSX tree instead of `<RouterProvider router={router} />`

#### Scenario: Fallback visual is correct

- **GIVEN** a lazy component is suspending (chunk loading in progress)
- **WHEN** React reaches the Suspense boundary
- **THEN** the fallback SHALL render a `<div className="flex items-center justify-center min-h-screen">` containing `<LoadingSpinner />`
