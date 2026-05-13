## Context

El sistema de autenticación backend está completamente implementado (Epic 1.1–1.6): endpoints de login, registro, logout, refresh y los interceptores Axios en el frontend. El `useAuthStore` (Zustand + persist) ya maneja login/logout/setTokens y persiste `user` y `token` en `localStorage`. El componente `ProtectedRoute` existe en `features/auth/components/` pero no está integrado al router. El Layout actual muestra solo el `CartBadge` en el header, sin información de sesión ni logout.

## Goals / Non-Goals

**Goals:**
- Implementar `LoginPage` y `RegisterPage` como páginas FSD bajo `frontend/src/pages/`
- Integrar `ProtectedRoute` al `router.tsx` para activar protección de rutas
- Agregar un componente `PublicOnlyRoute` (o guard inline) para redirigir usuarios ya autenticados fuera de `/login` y `/register`
- Agregar botón de logout al `Layout` con llamada al endpoint `POST /api/v1/auth/logout`
- Aprovechar el store y los interceptores ya implementados sin duplicar lógica

**Non-Goals:**
- Recuperación de contraseña o flujo de email verification
- Manejo de roles/RBAC en las rutas (ya cubierto por `RoleGuard` en `frontend-route-guards`)
- Cambio de contraseña o edición de perfil
- OAuth o login social

## Decisions

### D1: Feature Sliced Design — ¿Dónde viven las páginas de auth?

**Decisión:** Las páginas `/login` y `/register` viven en `frontend/src/pages/login/` y `frontend/src/pages/register/`. La lógica de llamada API se encapsula en `frontend/src/features/auth/api/auth.api.ts`.

**Alternativas consideradas:**
- Poner la lógica directo en la página: viola FSD, dificulta el reuso
- Crear un feature completo `features/auth/pages/`: innecesario — FSD distingue `pages/` como capa superior

**Razón:** FSD: `pages/` orquestan, `features/` encapsulan lógica y llamadas API. Las páginas usan el feature de auth, no lo replican.

---

### D2: TanStack Form para los formularios

**Decisión:** Usar `@tanstack/react-form` tal como establece la convención del proyecto (NO react-hook-form).

**Patrón aplicado:**
```tsx
const form = useForm({
  defaultValues: { email: '', password: '' },
  onSubmit: async ({ value }) => { /* llamada API */ },
})
```

**Validación:** Inline con el `validator` de TanStack Form (no Zod — simplicidad para forms de auth).

---

### D3: PublicOnlyRoute como componente separado

**Decisión:** Crear `PublicOnlyRoute` en `features/auth/components/`. Si el usuario está autenticado, redirige a `/`. Si no, renderiza `<Outlet />`.

**Alternativa considerada:** Guard inline en el router con una función. Menos legible y no reutilizable.

**Razón:** Simetría con `ProtectedRoute` — mismo patrón, fácil de razonar.

---

### D4: Llamada al logout endpoint antes de limpiar el store

**Decisión:** El botón de logout llama a `POST /api/v1/auth/logout` (fire-and-forget con catch silencioso) y luego llama `authStore.logout()` independientemente del resultado.

**Razón:** El backend puede revocar el refresh token en BD. Si el request falla (red, token ya expirado), el logout local igual procede — el usuario no queda "atrapado".

---

### D5: Estructura del router tras la integración

```
/
├── /login           → <PublicOnlyRoute> → <LoginPage>
├── /register        → <PublicOnlyRoute> → <RegisterPage>
└── <Layout>
    ├── / (index)    → <ProtectedRoute> → <HomePage>
    └── *            → <Navigate to="/" replace>
```

**Razón:** Mantiene el Layout solo para rutas autenticadas. `/login` y `/register` tienen su propio layout minimalista (fondo, card centrada).

---

### D6: Estética visual — Refined Minimal con warm accent

**Decisión:** Las páginas de auth tendrán un diseño limpio y refinado, con:
- Fondo `bg-gray-50` (consistente con el Layout existente)
- Card centrada con `shadow-md rounded-xl` usando el componente `Card` existente
- Color de acento en botón primario: naranja cálido (`#F97316` / `orange-500`) — coherente con una app de comida
- Tipografía: usar la fuente ya configurada del proyecto (Tailwind defaults)
- Transición suave en estados de loading/error

**Razón:** Consistencia con el sistema de diseño existente. La app de comida merece un toque warm y apetitoso, sin romper el sistema de colores de Tailwind ya en uso.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| `useAuthStore` persiste `token` pero no `refreshToken` — al recargar, el interceptor puede fallar si el access token expiró | El interceptor de Axios ya maneja el caso `!refreshToken` haciendo logout + redirect. El usuario tendrá que re-autenticarse si recarga con token expirado. Aceptable para esta fase. |
| Auto-login tras registro hace dos requests consecutivas (register + login) | El backend devuelve `access_token` + `refresh_token` en la respuesta de registro — usar esos tokens directamente sin llamar a `/auth/login` de nuevo. Verificar en el endpoint antes de implementar. |
| El botón de logout puede aparecer brevemente si el store hidrató tarde (flicker) | Usar `isAuthenticated` del store hidratado — Zustand `persist` es síncrono en su primera carga desde `localStorage`, el flicker es mínimo y aceptable. |

## Migration Plan

1. Crear `auth.api.ts` en `features/auth/api/` con funciones `loginUser`, `registerUser`, `logoutUser`
2. Crear `PublicOnlyRoute` en `features/auth/components/`
3. Crear `LoginPage` y `RegisterPage` en `pages/`
4. Modificar `router.tsx`: agregar rutas `/login` y `/register`, integrar `ProtectedRoute` en rutas privadas
5. Modificar `layout.tsx`: agregar botón de logout condicional

No hay migración de datos ni rollback especial — son páginas nuevas y modificaciones de routing. Si hay problemas, revertir `router.tsx` al estado anterior restaura el comportamiento previo.

## Open Questions

- ¿El endpoint `POST /api/v1/auth/register` devuelve tokens en la respuesta o solo el usuario? → Verificar en `backend/auth/router.py` durante implementación para decidir si se necesita auto-login extra o se pueden usar directamente los tokens de la respuesta.
- ¿La `LoginPage` debe mostrar un link a `/register` y viceversa? → Sí, estándar UX. Agregar como tarea de implementación.
