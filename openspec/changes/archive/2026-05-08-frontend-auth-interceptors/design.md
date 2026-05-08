## Context

El frontend tiene Axios instalado (setup 0.2) pero sin instancia centralizada. El `authStore` tiene `token` (access token) pero no `refreshToken`. Los interceptores de Axios necesitan acceder al store FUERA del árbol de React, por lo que deben usar `useAuthStore.getState()` (API de Zustand para acceso imperativo). La ruta `/auth/refresh` ya existe en el backend (1.3).

## Goals / Non-Goals

**Goals:**
- Centralizar todas las llamadas HTTP en una instancia Axios con baseURL configurable.
- Adjuntar el JWT automáticamente a cada request autenticada.
- Renovar el access token de forma transparente cuando expira (401), sin interrumpir la UX.
- Manejar concurrencia: un solo refresh aunque múltiples requests fallen simultáneamente.
- Estandarizar mensajes de error HTTP visibles al usuario.

**Non-Goals:**
- Persistir el `refreshToken` en localStorage (perdido al cerrar el tab — tradeoff de seguridad aceptado).
- Manejo de errores 5xx con retry automático.
- Toast/notificación UI de errores (eso va en cada feature con TanStack Query).

## Decisions

### 1. Axios instance en `shared/api/axios.ts`, acceso via `useAuthStore.getState()`

Los interceptores se configuran al inicializar el módulo, no dentro de un componente React. Zustand expone `useAuthStore.getState()` para acceso imperativo al estado del store fuera de React. Alternativa descartada: pasar el token como parámetro en cada llamada — rompe la centralización.

### 2. Queue para requests concurrentes durante refresh

Si 3 requests fallan con 401 simultáneamente, solo se ejecuta un `POST /auth/refresh`. Las otras 2 se encolan con una promesa que se resuelve cuando el refresh termina. Se usa un flag `isRefreshing: boolean` y un array `pendingQueue: Array<{resolve, reject}>`.

```
Request A → 401 → isRefreshing=false → inicia refresh → isRefreshing=true
Request B → 401 → isRefreshing=true  → encola promesa
Request C → 401 → isRefreshing=true  → encola promesa
Refresh OK → resolve queue → A, B, C se reintentan con nuevo token
Refresh FAIL → reject queue → todos van a logout + /login
```

### 3. authStore agrega `refreshToken` + `setTokens()`

`login(user, accessToken, refreshToken)` guarda ambos tokens. `setTokens(accessToken, refreshToken)` es el método que usa el interceptor tras un refresh exitoso sin recargar el estado del usuario. `logout()` limpia ambos. El `refreshToken` NO se persiste (fuera del `partialize` de Zustand persist).

### 4. Zustand persist middleware para el authStore

El `authStore` actual no usa persist. Lo agregamos con `partialize: (state) => ({ user: state.user, token: state.token })` — solo se persiste el access token (y el user para UX de "seguir logueado"). El refresh token no persiste intencionalmente.

### 5. `errors.ts` como mapa simple de código → mensaje

Un objeto `HTTP_ERROR_MESSAGES` con keys de status code. Un helper `getErrorMessage(error: AxiosError): string` que extrae el mensaje del backend si está en `error.response.data.detail`, con fallback al mapa por código. TanStack Query o los componentes individuales deciden cómo mostrar el mensaje (toast, inline, etc.).

## Risks / Trade-offs

- **refreshToken no persiste**: al refrescar la página, el refresh token se pierde y el usuario debe hacer login de nuevo aunque el access token (30 min) aún sea válido. Mitigación: aceptado por diseño — el access token en localStorage persiste, la sesión dura lo que dura el access token activo.
- **Race condition en logout**: si el refresh falla y múltiples requests encoladas reciben el reject, todas llaman a `logout()` al mismo tiempo. Mitigación: el `logout()` de Zustand es idempotente (set null sobre null no tiene efecto).

## Migration Plan

1. Agregar `refreshToken` + `setTokens()` + persist middleware al `authStore`.
2. Crear `frontend/src/shared/api/` con `axios.ts`, `errors.ts`, `index.ts`.
3. Crear `frontend/.env.example`.
4. Exportar la instancia desde `shared/`.
