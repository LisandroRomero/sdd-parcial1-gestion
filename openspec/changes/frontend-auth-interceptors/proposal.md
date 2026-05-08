## Why

El frontend tiene `authStore` con `hasRole()` y guards de rutas (1.5), pero no existe una instancia centralizada de Axios ni lógica para adjuntar el JWT a cada request. Tampoco hay renovación automática del access token cuando expira: el usuario ve errores 401 intermitentes en lugar de que la sesión se renueve de forma transparente. Esto bloquea el desarrollo de cualquier feature que haga llamadas autenticadas.

## What Changes

- Nuevo `frontend/src/shared/api/axios.ts` — instancia Axios centralizada con baseURL desde `VITE_API_BASE_URL`.
- **Request interceptor**: adjunta `Authorization: Bearer <token>` tomando el access token del `authStore` vía `useAuthStore.getState()`.
- **Response interceptor (401 auto-refresh)**: ante un 401, llama a `POST /auth/refresh` con el `refreshToken` del store, actualiza los tokens en el `authStore`, y reintenta la request original. Si el refresh también falla, llama a `logout()` y redirige a `/login`.
- **Queue de requests concurrentes**: si múltiples requests reciben 401 simultáneamente, solo se ejecuta un refresh — las demás se encolan y se reintentan al resolverse.
- Actualización del `authStore`: agregar `refreshToken: string | null` + actualizar `login()` para aceptar ambos tokens + agregar `setTokens()` para que el interceptor actualice los tokens tras el refresh.
- Nuevo `frontend/src/shared/api/errors.ts` — mapa de mensajes de error por código HTTP (400/403/404/429/500) para US-067.
- Archivo `frontend/.env.example` con `VITE_API_BASE_URL` y `VITE_MERCADOPAGO_PUBLIC_KEY`.

## Capabilities

### New Capabilities

- `frontend-axios-interceptors`: Instancia Axios con request interceptor (attach JWT) + response interceptor (auto-refresh 401 + queue de concurrencia).
- `frontend-http-error-handling`: Utilidad de mensajes de error estandarizados por código HTTP.

### Modified Capabilities

- `client-state`: El `authStore` necesita agregar `refreshToken` y `setTokens()` — cambio de estado del cliente.

## Impact

- **Frontend**: `frontend/src/shared/api/axios.ts` (nuevo), `frontend/src/shared/api/errors.ts` (nuevo), `frontend/src/shared/api/index.ts` (nuevo), `frontend/src/shared/lib/stores/auth.store.ts` (actualizar), `frontend/.env.example` (nuevo).
- **Sin cambios de backend**: los endpoints `/auth/refresh` y `/auth/logout` ya existen.
- **Dependencias FE existentes**: `axios` ya está en `package.json` (setup 0.2). `zustand` y `authStore` ya implementados (1.5).
