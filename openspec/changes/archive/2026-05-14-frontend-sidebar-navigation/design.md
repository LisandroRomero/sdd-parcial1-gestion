## Context

El frontend hoy renderiza un `Layout` unico con header/top-nav y un `main` centrado. Las rutas publicas (ej. catalogo) y privadas (home/pedidos/perfil/admin) reutilizan ese mismo `Layout`.

El crecimiento natural del sistema (mas secciones para admin y para usuario) vuelve poco escalable la navegacion horizontal. El cambio busca un patron de navegacion mas acorde a desktop (sidebar persistente) manteniendo una experiencia correcta en mobile (drawer).

Restricciones y contexto tecnico:

- React 18 + React Router (router central en `frontend/src/app/router.tsx`).
- Estilo con Tailwind.
- Feature-Sliced Design (Pages -> Features -> Entities -> Shared). La navegacion es transversal (shell), por lo que conviene ubicarla en `app/` (o un slice de shell si existe), sin romper imports.
- Guards existentes: `ProtectedRoute`, `AdminRoute`, `RoleGuard`.

## Goals / Non-Goals

**Goals:**

- Proveer un layout con sidebar (desktop) + top navbar complementaria, sin perder el contenido actual.
- Responsive:
  - Desktop: sidebar visible y opcionalmente colapsable.
  - Mobile/tablet: sidebar como drawer off-canvas con overlay.
- Integracion con el router actual para estado activo (ruta seleccionada) y navegacion.
- Accesibilidad:
  - Drawer con `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
  - Focus trap dentro del drawer; al cerrar, devolver foco al trigger.
  - Cerrar con `Escape` y click en overlay.
  - Navegacion por teclado en items.
- Acceso condicional:
  - Items visibles segun autenticacion.
  - Items admin visibles solo con rol `ADMIN` (y/o mas roles si se agrega a futuro).
- (Opcional) Persistir preferencia de colapso (collapsed/expanded) en almacenamiento local.

**Non-Goals:**

- Redisenar visual completo del sitio o crear un design system nuevo.
- Cambiar el modelo de permisos (RBAC) o los guards de rutas.
- Reestructurar rutas o renombrar paths existentes.
- Agregar analytics/telemetria.

## Decisions

### Decision: Mantener `Layout` como app shell e introducir estructura sidebar

Se mantiene el componente `Layout` como wrapper de `Outlet`, pero se reorganiza su markup:

- `header` (top navbar) sigue existiendo (branding, acciones globales como carrito/sesion)
- `aside` para sidebar en desktop
- `main` para contenido

Rationale:

- Minimiza impacto: el router ya usa `<Layout />` en rutas publicas/protegidas.
- Evita tocar cada pagina/feature.

Alternatives considered:

- Crear `PublicLayout` y `PrivateLayout` separados.
- Crear un `AppShell` nuevo y migrar rutas.

Se descarta por mayor churn; solo se considera si la diferencia entre nav publica y privada lo exige mas adelante.

### Decision: Configuracion de items via lista tipada + filtrado por contexto

Definir un modelo simple de item de navegacion (label, to, icon opcional, requiresAuth, roles opcionales) en una ubicacion del shell (ej. `app/navigation/*`), y renderizar:

- Un menu base con secciones (publicas y privadas)
- Filtrado por:
  - `isAuthenticated`
  - `user.roles`

Rationale:

- Centraliza navegacion y evita duplicar links en header/sidebar.
- Permite compartir logica entre desktop y drawer.

Alternatives considered:

- Hardcode de links en JSX (como hoy), duplicando para sidebar.
- Derivar items del router.

Derivar del router se evita porque el router contiene wrappers/guards y lazy imports; no es un buen source de menu.

### Decision: Drawer accesible sin dependencia externa

Implementar drawer con HTML + Tailwind y logica React:

- Overlay que bloquea scroll del body mientras esta abierto.
- Focus trap manual (tab cycle) o helper minimo en `shared`.

Rationale:

- Evita agregar dependencia externa solo para un drawer.

Tradeoff:

- Focus trap manual requiere cuidado y testeo manual.

### Decision: Persistencia de colapso opcional en `localStorage`

Si se implementa colapso, persistir `sidebarCollapsed` en `localStorage` con un key estable (ej. `ui.sidebar.collapsed`).

Rationale:

- Preferencia de UI, no del servidor.
- No debe mezclarse con estado de servidor (TanStack Query).

Alternatives considered:

- Zustand store persistido.

Se puede usar Zustand si ya existe un store de UI; si no, `localStorage` directo es suficiente.

## Risks / Trade-offs

- [Riesgo] Duplicacion de navegacion (header vs sidebar) -> Mitigacion: una unica fuente de items y dos renderers.
- [Riesgo] Drawer inaccesible (foco se escapa, no cierra con Escape) -> Mitigacion: implementar focus trap, devolver foco, y checklist de a11y.
- [Riesgo] Inconsistencias por roles -> Mitigacion: usar una funcion de filtrado central y roles declarativos por item.
- [Trade-off] Mantener header actual vs simplificarlo -> Mitigacion: header puede quedar mas liviano (trigger + acciones globales) cuando sidebar este presente.
