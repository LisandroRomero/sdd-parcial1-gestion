## 1. Routing (Public vs Protected)

- [x] 1.1 Actualizar `frontend/src/app/router.tsx` para que exista un branch publico en `path: "/"` con `Layout` e `index: HomePage`
  Evidencia: `frontend/src/app/router.tsx` — branch publico `path: '/'` con `element: <Layout />` y `{ index: true, element: <HomePage /> }`.
- [x] 1.2 Incluir las rutas del catalogo (ej. `/catalogo` y subrutas) como children del branch publico
  Evidencia: `frontend/src/app/router.tsx` — children `catalogo` y `catalogo/:id` bajo el branch publico.
- [x] 1.3 Mantener `PublicOnlyRoute` con redirect target `/` (sin introducir `/dashboard`)
  Evidencia: `frontend/src/features/auth/components/PublicOnlyRoute.tsx` — `Navigate to="/"` cuando `isAuthenticated`.
- [x] 1.4 Crear un branch protegido sibling en `path: "/"` envuelto por `ProtectedRoute`, SIN `index`, con children privados: `perfil`, `pedidos`, `checkout`, `admin/*`
  Evidencia: `frontend/src/app/router.tsx` — branch protegido `path: '/'` con `element: <ProtectedRoute />` y children `perfil`, `pedidos`, `checkout`, `admin/*`.
- [x] 1.5 Verificar que un usuario no autenticado navegando a `/perfil`, `/pedidos`, `/checkout`, `/admin/*` redirige a `/login`
  Evidencia: `frontend/src/features/auth/components/ProtectedRoute.tsx` — `Navigate to="/login"` si no hay sesion.
- [x] 1.6 Verificar que un usuario no autenticado navegando a `/` NO redirige a `/login`
  Evidencia: `frontend/src/app/router.tsx` — `HomePage` vive en el branch publico, no bajo `ProtectedRoute`.

## 2. Home (CTA a Catalogo)

- [x] 2.1 Asegurar que `HomePage` renderiza un CTA visible que navega a `/catalogo`
  Evidencia: `frontend/src/app/routes/home.tsx` — `Link to="/catalogo"` con boton "Ver catálogo".
- [x] 2.2 Revisar que el CTA funciona para usuario no autenticado (no requiere sesion)
  Evidencia: `frontend/src/app/router.tsx` — `/catalogo` esta en el branch publico (sin `ProtectedRoute`).

## 3. Navigation / Links privados

- [x] 3.1 Revisar links/menus visibles en `Layout`/header para que las entradas a rutas privadas sigan presentes pero queden correctamente protegidas por `ProtectedRoute`
  Evidencia: `frontend/src/app/navigation/navigation.config.ts` marca items privados con `requiresAuth: true` y `useFilteredNavSections` los filtra sin sesion; al estar las rutas ahora bajo `ProtectedRoute`, quedan protegidas.
- [x] 3.2 Confirmar que desde estado no autenticado, navegar manualmente a rutas privadas siempre redirige a `/login` (sin flashes de contenido)
  Evidencia: `frontend/src/features/auth/components/ProtectedRoute.tsx` hace redirect inmediato (sin renderizar `Outlet`).
- [x] 3.3 Agregar en el header un boton/link "Iniciar sesión" visible solo para usuarios no autenticados que navegue a `/login`
  Evidencia: `frontend/src/app/routes/layout.tsx` — render condicional `!isAuthenticated` con `navigate('/login')`.

## 4. Verificacion de flujos

- [x] 4.1 Flujo anonimo: `/` -> CTA a `/catalogo` -> intentar `/perfil` -> redirect a `/login`
  Evidencia: branch publico incluye `/` y `/catalogo`; branch protegido contiene `/perfil` y redirige a `/login` si no auth.
- [x] 4.2 Flujo autenticado: `/` -> `/perfil` y `/pedidos` renderizan normalmente; `/login` y `/register` redirigen a `/`
  Evidencia: `ProtectedRoute` permite `Outlet` con sesion; `PublicOnlyRoute` redirige a `/` con sesion.
