## 1. API Layer — Feature Auth

- [x] 1.1 Crear `frontend/src/features/auth/api/auth.api.ts` con funciones `loginUser(email, password)`, `registerUser(nombre, email, password)` y `logoutUser()` usando la instancia Axios de `shared/api/axios.ts`
- [x] 1.2 Verificar qué retorna `POST /api/v1/auth/register` (si incluye tokens o solo el usuario) leyendo `backend/auth/router.py` y ajustar la función `registerUser` acordemente
- [x] 1.3 Exportar las funciones desde `frontend/src/features/auth/index.ts`

## 2. PublicOnlyRoute Guard

- [x] 2.1 Crear `frontend/src/features/auth/components/PublicOnlyRoute.tsx` que redirija a `/` si `isAuthenticated === true`, renderice `<Outlet />` si no
- [x] 2.2 Exportar `PublicOnlyRoute` desde `frontend/src/features/auth/index.ts` junto a `ProtectedRoute`

## 3. Página de Login

- [x] 3.1 Crear directorio `frontend/src/pages/login/` con `index.tsx` (barrel) y `LoginPage.tsx`
- [x] 3.2 Implementar `LoginPage` con `useForm` de TanStack Form — campos: `email` (type email, required, validación de formato) y `password` (type password, required)
- [x] 3.3 Conectar `onSubmit` del formulario: llamar a `loginUser()`, en éxito llamar a `useAuthStore().login()` con los datos y redirigir a `/` con `useNavigate`
- [x] 3.4 Manejar errores HTTP: mostrar "Email o contraseña incorrectos" en HTTP 401, mensaje genérico para otros errores
- [x] 3.5 Mostrar estado de loading en el botón Submit durante el request (deshabilitar para evitar doble envío)
- [x] 3.6 Agregar link "¿No tenés cuenta? Registrate" que navega a `/register`
- [x] 3.7 Aplicar diseño: Card centrada en pantalla completa (`min-h-screen flex items-center justify-center bg-gray-50`), usar componente `Card` de `shared/components`, botón primario en naranja (`bg-orange-500 hover:bg-orange-600`), componente `Input` existente

## 4. Página de Registro

- [x] 4.1 Crear directorio `frontend/src/pages/register/` con `index.tsx` (barrel) y `RegisterPage.tsx`
- [x] 4.2 Implementar `RegisterPage` con `useForm` de TanStack Form — campos: `nombre` (required), `email` (required, formato email), `password` (required, mínimo 8 chars), `confirmPassword` (required, debe coincidir con `password`)
- [x] 4.3 Agregar validación cross-field: si `confirmPassword !== password`, mostrar "Las contraseñas no coinciden"
- [x] 4.4 Conectar `onSubmit`: llamar a `registerUser()`, en éxito llamar a `useAuthStore().login()` con los tokens/datos retornados y redirigir a `/`
- [x] 4.5 Manejar errores del servidor: mostrar el mensaje del backend (ej. "Email ya registrado") o mensaje genérico
- [x] 4.6 Mostrar estado de loading en el botón Submit durante el request
- [x] 4.7 Agregar link "¿Ya tenés cuenta? Iniciá sesión" que navega a `/login`
- [x] 4.8 Aplicar mismo diseño que `LoginPage` (Card centrada, mismo esquema de colores)

## 5. Logout en el Header

- [x] 5.1 Modificar `frontend/src/app/routes/layout.tsx` para importar `useAuthStore`
- [x] 5.2 Agregar sección condicional en el header: si `isAuthenticated`, mostrar `"Hola, {user.nombre}"` y botón "Cerrar sesión"
- [x] 5.3 Implementar handler `handleLogout`: llamar a `logoutUser()` (con catch silencioso), luego llamar a `useAuthStore().logout()` y redirigir a `/login` con `useNavigate`
- [x] 5.4 Estilizar el botón de logout como variante ghost/outline para no competir visualmente con el `CartBadge`

## 6. Integración en el Router

- [x] 6.1 Modificar `frontend/src/app/router.tsx`: agregar rutas `/login` y `/register` bajo `PublicOnlyRoute` con lazy loading (`lazy(() => import('../pages/login'))`)
- [x] 6.2 Envolver la ruta `/` (Layout) con `ProtectedRoute` para que todas las rutas del layout requieran autenticación
- [x] 6.3 Verificar que el fallback `*` → `<Navigate to="/" replace>` siga funcionando dentro del contexto protegido
- [x] 6.4 Probar el flujo completo: usuario no autenticado → redirige a `/login` → login exitoso → redirige a `/` → logout → redirige a `/login`

## 7. Verificación y Ajustes Finales

- [x] 7.1 Verificar que la persistencia funcione: autenticarse, recargar la página, confirmar que `isAuthenticated` se restaura desde `localStorage` y no redirige a login
- [x] 7.2 Verificar que usuarios autenticados que navegan a `/login` o `/register` sean redirigidos a `/`
- [x] 7.3 Revisar accesibilidad básica: `htmlFor` en labels, `aria-invalid` en campos con error, `role="alert"` en mensajes de error
- [x] 7.4 Verificar que los formularios no hagan doble submit (botón disabled durante loading)
