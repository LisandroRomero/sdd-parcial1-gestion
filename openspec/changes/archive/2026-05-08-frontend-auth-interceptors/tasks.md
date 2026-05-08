## 1. authStore — Actualizar estado y persistencia

- [x] 1.1 Agregar `refreshToken: string | null` al `AuthState` interface en `auth.store.ts`
- [x] 1.2 Agregar método `setTokens(accessToken: string, refreshToken: string): void` al `AuthState` interface
- [x] 1.3 Actualizar `login()` para aceptar `(user: User, accessToken: string, refreshToken: string)` y setear los 3 campos
- [x] 1.4 Actualizar `logout()` para limpiar `refreshToken` a null
- [x] 1.5 Agregar zustand persist middleware con `partialize: (state) => ({ user: state.user, token: state.token })` — NO persistir `refreshToken`

## 2. Axios instance

- [x] 2.1 Crear directorio `frontend/src/shared/api/`
- [x] 2.2 Crear `frontend/src/shared/api/axios.ts` con instancia Axios y baseURL desde `import.meta.env.VITE_API_BASE_URL`
- [x] 2.3 Agregar **request interceptor**: extraer `token` de `useAuthStore.getState()` y adjuntar `Authorization: Bearer <token>` si existe
- [x] 2.4 Agregar **response interceptor** con lógica de 401 auto-refresh:
  - Flag `isRefreshing: boolean` y queue `pendingQueue: Array<{resolve, reject}>`
  - Si 401 y NO es la ruta `/auth/refresh`: obtener `refreshToken` de `useAuthStore.getState()`, si no hay → `logout()` + redirect a `/login`
  - Si `isRefreshing`: encolar la request en `pendingQueue` y retornar una promesa
  - Si no: setear `isRefreshing = true`, llamar `POST /auth/refresh`, en éxito → `setTokens()` + resolver queue + reintentar original; en error → rechazar queue + `logout()` + redirect a `/login`

## 3. Error handler

- [x] 3.1 Crear `frontend/src/shared/api/errors.ts` con mapa `HTTP_ERROR_MESSAGES` (400/403/404/429/500) y función `getErrorMessage(error: AxiosError | unknown): string` que devuelve `error.response.data.detail` si existe, o el mensaje del mapa, o "Sin conexión" si no hay response

## 4. Barrel exports

- [x] 4.1 Crear `frontend/src/shared/api/index.ts` exportando la instancia `api` y `getErrorMessage`

## 5. Entorno

- [x] 5.1 Crear `frontend/.env.example` con:
  ```
  VITE_API_BASE_URL=http://localhost:8000/api/v1
  VITE_MERCADOPAGO_PUBLIC_KEY=TEST-xxx
  ```
- [x] 5.2 Crear `frontend/.env` (gitignoreado) con los mismos valores para desarrollo local

## 6. Verificación

- [x] 6.1 Verificar que request al backend incluye el header `Authorization: Bearer` cuando hay token en el store
- [x] 6.2 Verificar que request sin token NO incluye header Authorization
- [x] 6.3 Verificar que `getErrorMessage` retorna el `detail` del backend para errores conocidos
- [x] 6.4 Verificar que `getErrorMessage` retorna mensajes de fallback para 403, 404, 429, 500
