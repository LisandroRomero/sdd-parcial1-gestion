## Context

El frontend Food Store está construido con React 18 + TypeScript + Vite, siguiendo Feature-Sliced Design (FSD). Actualmente no existe ninguna capa de estado del cliente. La aplicación tiene routing básico y componentes UI compartidos, pero ninguna store para manejar sesión, carrito, pagos o preferencias de interfaz.

El proyecto ya definió en su roadmap (CHANGES.md) que Zustand v4 será el gestor de estado del cliente, con TanStack Query para estado del servidor. Este diseño implementa la primera parte.

## Goals / Non-Goals

**Goals:**
- Proveer 4 stores tipadas con Zustand v4: auth, cart, payment, ui
- Persistencia selectiva vía `persist` middleware (cartStore y uiStore)
- API limpia y predecible para los consumidores (components, features, pages)
- Separación clara de responsabilidades: estado del cliente ≠ estado del servidor
- Typescript estricto: interfaces de estado y acciones explícitas

**Non-Goals:**
- NO implementar lógica de autenticación (login/logout API calls) — eso pertenece al feature de auth
- NO implementar lógica de pagos contra MercadoPago — eso pertenece al feature de pagos
- NO integrar TanStack Query — eso es un cambio independiente
- NO crear hooks de autenticación (useAuth) — se crearán cuando existan los features

## Decisions

### 1. Zustand v4 sobre Redux o Context API

| Alternativa | Veredicto |
|---|---|
| **Zustand v4** | ✅ Elegido. API minimalista, suscripciones granulares (sin re-renders innecesarios), persist middleware built-in, TypeScript first. |
| Redux Toolkit | ❌ Overkill para el alcance. Más boilerplate (slices, actions, dispatch). La aplicación no justifica la complejidad de Redux. |
| Context API | ❌ Re-renders全局es (toda la app se re-renderiza cuando cambia el contexto). No tiene persist middleware. Escala mal con múltiples stores. |
| Jotai / Recoil | ❌ Modelo atómico interesante pero menos adopción en el equipo. Zustand es más predecible para un equipo que recién arranca. |

### 2. 4 stores separados vs 1 mega-store

**Decisión: 4 stores independientes.** Cada store tiene un dominio claramente delimitado y ciclos de actualización distintos. Un solo store gigante haría que cualquier cambio dispare re-renders innecesarios aunque el componente solo consuma una parte. Además, la persistencia selectiva (solo cart y ui) es más fácil de configurar por store.

### 3. Persistencia: solo cartStore y uiStore

- **authStore**: NO persistir. El token JWT se maneja via httpOnly cookie o variable en memoria (decisión de seguridad). El refresh token vive en BD. La store refleja el estado actual de la sesión en memoria.
- **cartStore**: SÍ persistir (localStorage). El carrito sobrevive a refrescos de página y cierres de navegador. Es la expectativa del usuario.
- **paymentStore**: NO persistir. El estado de pago es transitorio y sensible. Si el usuario refresca, debe consultar el estado real contra el backend.
- **uiStore**: SÍ persistir (localStorage). Preferencias de UI (sidebar, tema) deben mantenerse entre sesiones.

### 4. Estructura de archivos

```
shared/lib/stores/
├── auth.store.ts
├── cart.store.ts
├── payment.store.ts
├── ui.store.ts
└── index.ts          # barrel export
```

Cada store exporta:
- El hook tipado (`useAuthStore`, `useCartStore`, etc.)
- El store object para acceso fuera de componentes (`authStore`, `cartStore`, etc.)
- Tipos de estado y acciones (`AuthState`, `CartItem`, etc.)

### 5. Patrón de acciones colocalizadas

Las funciones que modifican el estado (acciones) viven dentro del store, no en archivos separados. Esto mantiene el store auto-contenido y facilita el testing. Para lógica asincrónica (ej: llamar a un endpoint y luego actualizar el store), se usará `set` dentro de funciones del store o hooks externos que consuman el store.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| **Persistencia corrompida**: si cambia la estructura del store, datos viejos en localStorage pueden romper la app | Usar `version` + `migrate` de persist middleware. Versión inicial 1. |
| **Falta de sincronización**: cartStore persistido podría quedar out of sync con el backend (stock desactualizado) | El cartStore es cliente-only. La validación de stock ocurre al crear el pedido (backend). El store refleja el intento del usuario, no una garantía. |
| **Multiple stores = múltiples imports**: consumidores necesitan importar de distintos archivos | Barrel export resuelve: `import { useAuthStore, useCartStore } from '@/shared/lib/stores'` |
| **Over-persistencia**: persistir demasiado puede exponer datos sensibles | Solo persistimos cartStore y uiStore. authStore y paymentStore no persisten nada. |
