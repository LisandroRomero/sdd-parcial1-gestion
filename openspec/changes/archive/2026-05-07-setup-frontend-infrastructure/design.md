## Context

El proyecto Food Store necesita infraestructura frontend para soportar todas las funcionalidades planificadas. Actualmente no existe configuración inicial de React, Vite, TypeScript ni Tailwind. Este diseño establece la arquitectura base y las decisiones técnicas para el frontend.

## Goals / Non-Goals

**Goals:**

- Establecer estructura FSD clara y escalable
- Configurar herramientas de desarrollo modernas (Vite, TypeScript, ESLint, Prettier)
- Definir design tokens y componentes base reutilizables
- Implementar routing base con React Router v6

**Non-Goals:**

- No implementar features de negocio (auth, catálogo, pedidos, etc.)
- No crear componentes de UI complejos — solo base
- No configurar testing (ver change 8.2)

## Decisiones

### Decisión 1: Vite sobre CRA

**Elección**: Vite

**Alternativas**: Create React App (CRA), Next.js, Webpack

**Justificación**: Vite ofrece mejor DX con HMR rápido, build optimizado con esbuild, y soporte nativo TypeScript sin configuración adicional. CRA está deprecado.

### Decisión 2: Feature-Sliced Design (FSD)

**Elección**: FSD

**Alternativas**: Feature folders simples, DDD por dominio, Atomic Design

**Justificación**: FSD escala bien para proyectos medianos-grandes, encapsula lógica por feature, y es agnóstico del framework. Define claramente la dirección de imports (solo hacia abajo).

### Decisión 3: Tailwind CSS v4

**Elección**: Tailwind v4 con CSS-first config

**Alternativas**: Tailwind v3 con config file, CSS Modules, Styled Components

**Justificación**: Tailwind v4 simplifica la configuración con CSS variables nativas, tiene mejor performance, y el equipo ya tiene experiencia.

### Decisión 4: TypeScript Strict

**Elección**: TypeScript con strict mode

**Justificación**: Mejora calidad del código, reduce bugs en runtime, mejor IDE support. El costo inicial se recupera rápidamente.

## Estructura de carpetas FSD

```
frontend/
├── app/                    # Providers, router, App.tsx
├── pages/                  # Page components (usan features)
│   └── MainPage.tsx
├── features/               # Lógica de negocio encapsulada (pendiente)
├── entities/               # Modelos de dominio (pendiente)
└── shared/                 # UI base, utils, hooks reutilizables
    ├── components/          # Componentes base (Button, Input, Card, etc.)
    ├── ui/                 # UI primitives
    ├── hooks/              # Hooks reutilizables
    └── lib/                # Utils, helpers
```

## Design Tokens (Tailwind)

```css
:root {
  --color-primary: #...;
  --color-secondary: #...;
  --font-sans: Inter, system-ui, sans-serif;
  --spacing-base: 4px;
}
```

## Riesgos / Trade-offs

| Riesgo | Mitigation |
|--------|------------|
| Curva de aprendizaje FSD | Documentar convenciones en README.md del frontend |
| Configuración inicial compleja | Seguir templates probados, minimizar personalización inicial |
| Tailwind genera CSS genérico | Implementar design tokens consistentes desde el inicio |

## Open Questions

- ¿Se usará shadcn/ui como base de componentes? (Pendiente — decisión para Epic 07)
- ¿Se configurará SSR en el futuro? (No para MVP — arquitectura SPA pura)