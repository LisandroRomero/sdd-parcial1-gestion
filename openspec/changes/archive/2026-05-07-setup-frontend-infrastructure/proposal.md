## Por qué

El proyecto **Food Store** requiere una base sólida de infraestructura frontend para soportar todas las funcionalidades planificadas (autenticación, catálogo, carrito, pedidos, pagos, admin). Actualmente no existe configuración inicial de React, Vite, TypeScript ni Tailwind. Sin esta infraestructura base, no es posible implementar ninguna feature del frontend.

**Problema**: Sin setup de frontend, todo el desarrollo de la interfaz de usuario queda bloqueado.

**Por qué ahora**: El Sprint 0 es transversal a toda la aplicación. Sin esta infraestructura, no se puede avanzar con ningún change que tenga componente frontend (Epics 01-08).

---

## Qué cambia

- Configuración inicial completa de **React 18** con **TypeScript**
- **Vite** como bundler y dev server (reemplaza CRA)
- **Tailwind CSS v4** con diseño tokens del proyecto
- **Feature-Sliced Design (FSD)**: estructura de carpetas app/, pages/, features/, entities/, shared/
- Routing base con **React Router v6**
- Configuración de **linting** (ESLint + Prettier) y type checking (TypeScript strict)
- Configuración de variables de entorno para desarrollo
- Archivos de configuración base: `tsconfig.json`, `vite.config.ts`, `tailwind.config.ts`, `postcss.config.js`

---

## Capabilities

### New Capabilities

- `frontend-scaffolding`: Estructura base FSD con configuración de herramientas (Vite, TypeScript, Tailwind, ESLint, Prettier)
- `frontend-routing`: Routing base con React Router v6 y estructura de páginas
- `frontend-tailwind-design-system`: Design tokens y componentes base reutilizables
- `frontend-error-handling-base`: Manejo de errores y estado de carga base para toda la app

### Modified Capabilities

*(Ninguna — este es un change de infraestructura pura)*

---

## Impacto

| Área | Impacto |
|------|---------|
| **Código nuevo** | `frontend/` completo (excepto features/features) |
| **Modificaciones** | Ninguna (no hay código existente en frontend/) |
| **Dependencias externas** | React 18, Vite, TypeScript, Tailwind CSS, React Router v6, ESLint, Prettier |
| **Artefactos externos** | Ninguno |
| **Riesgo** | Bajo — es configuración estándar de la industria |

---

## Decisiones de diseño

- **Vite** sobre CRA por velocidad de DX y soporte nativo de TypeScript
- **FSD** como arquitectura para encapsular lógica por feature
- **Tailwind v4** con CSS-first config (sin tailwind.config.js tradicional)
- **Strict TypeScript** habilitado desde el inicio
