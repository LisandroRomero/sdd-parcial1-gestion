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

## Guía de Estados de UI

Usá estos patrones en pantallas que consumen datos remotos:

- `LoadingSpinner` o skeletons para carga inicial.
- `EmptyState` cuando no hay datos, con CTA claro por pantalla.
- `ErrorMessage` para errores inline, siempre con `getErrorMessage(error)`.
- `OfflineMessage` cuando `useOffline()` devuelve `true`.
- `NoPermissionMessage` cuando `getAuthErrorStatus(error)` devuelve `401` o `403`.

Reglas prácticas:

- Si hay `data` previa, no reemplaces la vista entera por error de refetch.
- Si la query falla por primera vez y no hay data, mostr
  `ErrorMessage` con `onRetry`.
- Si la pantalla depende de una acción crítica, deshabilitá el CTA mientras no haya conexión.
- No uses `error.message` directo en UI.

### TanStack Query

Separá carga inicial de errores de refetch:

```tsx
const { data, isLoading, isError, error, refetch } = useQuery(...)

if (isLoading && !data) return <LoadingSpinner />

if (isError && !data) {
  const status = getAuthErrorStatus(error)
  return status ? (
    <NoPermissionMessage status={status} />
  ) : (
    <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
  )
}

return (
  <>
    {data?.items.length === 0 ? <EmptyState title="Sin resultados" /> : <Results data={data} />}
    {isError && data && <ErrorMessage compact message={getErrorMessage(error)} onRetry={refetch} />}
  </>
)
```

### Ejemplos del repo

- `frontend/src/pages/catalogo/CatalogoPage.tsx` muestra `OfflineMessage`, `ErrorMessage` inline y CTA para limpiar filtros.
- `frontend/src/pages/checkout/CheckoutPage.tsx` mapea `401/403` a `NoPermissionMessage` y bloquea la acción si no hay conexión.
- `frontend/src/pages/pedidos/PedidoDetailPage.tsx` conserva la vista si falla una mutación y muestra el error cerca del CTA.

## Enlaces

- [Documentación de React](https://react.dev)
- [Documentación de Vite](https://vitejs.dev)
- [Documentación de Tailwind](https://tailwindcss.com)
- [Feature-Sliced Design](https://feature-sliced.design)
