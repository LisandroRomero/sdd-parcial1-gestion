## 1. Conectar RouterLoader en Providers

- [x] 1.1 Cambiar import en `providers.tsx` de `{ router }` a `{ RouterLoader }`
- [x] 1.2 Reemplazar `<RouterProvider router={router} />` por `<RouterLoader />` en el JSX de `Providers`
- [x] 1.3 Verificar que `RouterLoader` se renderiza correctamente: abrir la app, navegar entre páginas, confirmar que el error de Suspense ya no aparece
