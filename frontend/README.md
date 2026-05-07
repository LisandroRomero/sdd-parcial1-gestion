# Food Store Frontend

Frontend de la aplicación Food Store, construido con React 18, TypeScript, Vite y Tailwind CSS.

## Estructura del Proyecto

El proyecto sigue la arquitectura **Feature-Sliced Design (FSD)**:

```
frontend/src/
├── app/                    # Configuración principal de la app
│   ├── providers.tsx       # Providers (Router, etc.)
│   ├── router.tsx          # Configuración de rutas
│   └── routes/             # Componentes de página
├── pages/                  # Page components (usan features)
├── features/               # Lógica de negocio encapsulada
├── entities/               # Modelos de dominio
└── shared/                 # UI base, utils, hooks reutilizables
    ├── components/         # Componentes base (Button, Input, Card)
    ├── ui/                 # UI primitives (LoadingSpinner, etc.)
    ├── hooks/              # Hooks reutilizables
    └── lib/                # Utils, helpers
```

## Requisitos Previos

- Node.js 18+ 
- npm 9+

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env
```

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Iniciar servidor de desarrollo |
| `npm run build` | Construir para producción |
| `npm run preview` | Previsualizar build de producción |
| `npm run lint` | Verificar código con ESLint |

## Tecnologías

- **React 18** - Librería de UI
- **TypeScript** - Tipado estático
- **Vite** - Bundler y dev server
- **Tailwind CSS v4** - Utilidades de CSS
- **React Router v6** - Navegación

## Convenciones

### Imports

- Usar alias de path: `@/` para `src/`
- Imports absolutos dentro de cada capa FSD
- No importar hacia arriba en la estructura FSD

### Nomenclatura

- Componentes: PascalCase (`Button.tsx`)
- Hooks: camelCase con prefijo `use` (`useAuth.ts`)
- Utils: camelCase (`formatCurrency.ts`)
- Constantes: SCREAMING_SNAKE_CASE

### Design Tokens

Los tokens de diseño están definidos en `src/index.css` usando la sintaxis `@theme` de Tailwind v4.

## Enlaces

- [Documentación de React](https://react.dev)
- [Documentación de Vite](https://vitejs.dev)
- [Documentación de Tailwind](https://tailwindcss.com)
- [Feature-Sliced Design](https://feature-sliced.design)