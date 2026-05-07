# Tareas de Implementación — setup-frontend-infrastructure

## 1. Configuración de Proyecto Base

- [x] 1.1 Crear carpeta `frontend/` en la raíz del proyecto
- [x] 1.2 Crear `package.json` con dependencias: react@18, react-dom@18, react-router-dom@6, vite@5, typescript, @types/react, @types/react-dom
- [x] 1.3 Crear `tsconfig.json` con strict mode habilitado
- [x] 1.4 Crear `tsconfig.node.json` para configuración de Vite
- [x] 1.5 Crear `vite.config.ts` con plugin de React y configuración base
- [x] 1.6 Crear `index.html` base con div#root

## 2. Tailwind CSS v4

- [x] 2.1 Instalar tailwindcss, @tailwindcss/vite
- [x] 2.2 Crear `src/index.css` con directivas Tailwind y design tokens
- [x] 2.3 Configurar design tokens para colores, tipografía y espaciado
- [x] 2.4 Crear `postcss.config.js` si es necesario

## 3. ESLint y Prettier

- [x] 3.1 Crear `.eslintrc.json` con configuración React/TypeScript
- [x] 3.2 Crear `.prettierrc` con convenciones de formateo
- [x] 3.3 Crear `.eslintignore` y `.prettierignore`

## 4. Estructura FSD — Carpetas Base

- [x] 4.1 Crear carpeta `app/` con `App.tsx` y `main.tsx`
- [x] 4.2 Crear carpeta `pages/` vacía con archivo `.gitkeep`
- [x] 4.3 Crear carpeta `features/` vacía con archivo `.gitkeep`
- [x] 4.4 Crear carpeta `entities/` vacía con archivo `.gitkeep`
- [x] 4.5 Crear carpeta `shared/` con subcarpetas: components/, ui/, hooks/, lib/

## 5. Routing Base

- [x] 5.1 Crear `app/providers.tsx` con RouterProvider
- [x] 5.2 Crear `app/router.tsx` con createBrowserRouter y rutas base
- [x] 5.3 Crear `app/routes/home.tsx` como página de inicio placeholder
- [x] 5.4 Crear `app/routes/layout.tsx` con Outlet y estructura base
- [x] 5.5 Configurar lazy loading para rutas con React.lazy y Suspense

## 6. Componentes Base — shared/components/

- [x] 6.1 Crear `Button.tsx` con variants: primary, secondary, outline, ghost
- [x] 6.2 Crear `Input.tsx` con soporte para label, error y helper text
- [x] 6.3 Crear `Card.tsx` con header, content, footer slots
- [x] 6.4 Exportar todos los componentes desde `shared/components/index.ts`

## 7. Estado de Carga y Errores — shared/ui/

- [x] 7.1 Crear `LoadingSpinner.tsx` con animación de spinner
- [x] 7.2 Crear `ErrorMessage.tsx` para mostrar mensajes de error
- [x] 7.3 Crear `EmptyState.tsx` con icono y mensaje para estados vacíos
- [x] 7.4 Exportar desde `shared/ui/index.ts`

## 8. Error Boundary

- [x] 8.1 Crear `ErrorBoundary.tsx` usando React Error Boundary
- [x] 8.2 Integrar ErrorBoundary en `app/providers.tsx`
- [x] 8.3 Crear página de error fallback con botón de retry

## 9. Archivos de Configuración Finales

- [x] 9.1 Crear `.env.example` con variables de entorno base (VITE_API_URL)
- [x] 9.2 Crear `.gitignore` con patrones para node_modules, dist, .env
- [x] 9.3 Crear `frontend/README.md` con instrucciones de setup y estructura FSD

## 10. Verificación

- [x] 10.1 Verificar que `npm install` funciona sin errores
- [x] 10.2 Verificar que `npm run dev` inicia el servidor de desarrollo
- [x] 10.3 Verificar que TypeScript no tiene errores de tipo
- [x] 10.4 Verificar que ESLint no reporta errores
