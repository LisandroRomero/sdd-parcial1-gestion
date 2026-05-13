## Why

El backend de autenticación (login, registro, logout, refresh) está completamente implementado, pero el frontend carece de las páginas y la navegación necesarias para que los usuarios interactúen con él. Sin `LoginPage`, `RegisterPage` y rutas protegidas funcionales, la autenticación es inutilizable desde el navegador.

## What Changes

- **Nueva página `/login`**: Formulario email + password con TanStack Form. Llama a `POST /api/v1/auth/login`, guarda tokens en `useAuthStore`, redirige a `/` tras éxito, muestra errores 401 como "Email o contraseña incorrectos".
- **Nueva página `/register`**: Formulario nombre + email + password + confirmación. Llama a `POST /api/v1/auth/register`, hace auto-login tras registro exitoso, redirige a `/`.
- **Logout en header**: Botón visible solo cuando el usuario está autenticado. Llama a `POST /api/v1/auth/logout`, limpia `useAuthStore`, redirige a `/login`.
- **Rutas protegidas activas**: El componente `ProtectedRoute` ya existe; se integra en `router.tsx` para envolver rutas que requieren autenticación.
- **Redirect de rutas públicas**: Si el usuario está autenticado e intenta acceder a `/login` o `/register`, se redirige automáticamente a `/`.
- **Persistencia de sesión**: `useAuthStore` ya usa `persist` con `localStorage`; al cargar la app con token almacenado, el usuario no debe pasar por login nuevamente.

## Capabilities

### New Capabilities

- `auth-login-page`: Página de Login (`/login`) con formulario, llamada al endpoint, manejo de errores y redirect.
- `auth-register-page`: Página de Registro (`/register`) con formulario multi-campo, auto-login tras registro y redirect.
- `auth-logout-button`: Botón de Logout en el header con llamada al endpoint y limpieza del store.
- `auth-public-route-guard`: Redirect automático para usuarios ya autenticados que intentan acceder a `/login` o `/register`.

### Modified Capabilities

- `frontend-route-guards`: Se activan las rutas protegidas en el router — `ProtectedRoute` ya existe pero no está integrado en `router.tsx`. Se agrega la integración real.

## Impact

- **Archivos nuevos**: `frontend/src/pages/login/`, `frontend/src/pages/register/`, `frontend/src/features/auth/api/auth.api.ts` (si no existe)
- **Archivos modificados**: `frontend/src/app/router.tsx` (integrar `ProtectedRoute` y agregar rutas `/login`, `/register`), `frontend/src/app/routes/layout.tsx` (agregar botón de logout)
- **Dependencias existentes utilizadas**: `useAuthStore` (login/logout/setTokens), instancia Axios de `shared/api/axios.ts`, `ProtectedRoute` de `features/auth/components/`
- **Sin cambios en backend**: Todos los endpoints necesarios ya están implementados
- **Sin nuevas dependencias npm**: TanStack Form, React Router v6, Zustand y Axios ya están disponibles
