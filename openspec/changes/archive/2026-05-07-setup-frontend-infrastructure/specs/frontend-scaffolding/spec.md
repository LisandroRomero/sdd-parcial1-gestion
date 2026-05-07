## ADDED Requirements

### Requirement: El proyecto DEBE usar Vite como bundler y dev server
El proyecto DEBE utilizar Vite como herramienta de bundling y servidor de desarrollo para garantizar tiempos de inicio rápidos y experiencia de desarrollo óptima.

#### Scenario: Iniciar el servidor de desarrollo
- **WHEN** El desarrollador ejecuta el comando `npm run dev`
- **THEN** Vite inicia el servidor de desarrollo en el puerto configurado y sirve los archivos de la aplicación

#### Scenario: Construir la aplicación para producción
- **WHEN** El desarrollador ejecuta el comando `npm run build`
- **THEN** Vite genera los archivos optimizados para producción en la carpeta `dist/`

---

### Requirement: El proyecto DEBE usar TypeScript con strict mode habilitado
El proyecto DEBE utilizar TypeScript con el modo estricto habilitado para garantizar type-safety en todo el código.

#### Scenario: Verificar configuración de TypeScript
- **WHEN** Se revisa el archivo `tsconfig.json`
- **THEN** La opción `strict` está establecida en `true` y todas las opciones de strict están habilitadas

#### Scenario: Compilación con errores de tipo
- **WHEN** El código contiene errores de tipo que violan las reglas de strict mode
- **THEN** TypeScript genera un error en tiempo de compilación y el build falla

---

### Requirement: El proyecto DEBE usar React 18
El proyecto DEBE utilizar React versión 18 como biblioteca de UI.

#### Scenario: Instalación de dependencias
- **WHEN** Se instalan las dependencias del proyecto
- **THEN** La versión de `react` y `react-dom` en `package.json` es 18.x

#### Scenario: Renderizado con Concurrent Features
- **WHEN** Se renderiza un componente React
- **THEN** El renderizado utiliza las APIs de React 18 incluyendo Concurrent Features si es necesario

---

### Requirement: El proyecto DEBE seguir Feature-Sliced Design (FSD)
El proyecto DEBE seguir la metodología Feature-Sliced Design para estructurar el código frontend.

#### Scenario: Estructura de carpetas FSD
- **WHEN** Se examina la estructura de carpetas del directorio `frontend/`
- **THEN** Existen las carpetas: `app/`, `pages/`, `features/`, `entities/`, `shared/`

#### Scenario: Convenciones de imports FSD
- **WHEN** Se importan módulos entre capas
- **THEN** Los imports fluyen unidireccionalmente desde capas superiores hacia inferiores (Pages → Features → Entities → Shared)

---

### Requirement: La estructura DEBE incluir: app/, pages/, features/, entities/, shared/
La estructura del proyecto frontend DEBE contener las capas fundamentales de FSD.

#### Scenario: Carpeta app/
- **WHEN** Se examina la carpeta `frontend/app/`
- **THEN** Contiene la configuración raíz de la aplicación, providers y router

#### Scenario: Carpeta pages/
- **WHEN** Se examina la carpeta `frontend/pages/`
- **THEN** Contiene los componentes de página que definen rutas principales

#### Scenario: Carpeta features/
- **WHEN** Se examina la carpeta `frontend/features/`
- **THEN** Contiene la lógica de negocio encapsulada por feature (auth, productos, pedidos, etc.)

#### Scenario: Carpeta entities/
- **WHEN** Se examina la carpeta `frontend/entities/`
- **THEN** Contiene los modelos de dominio y tipos compartidos

#### Scenario: Carpeta shared/
- **WHEN** Se examina la carpeta `frontend/shared/`
- **THEN** Contains componentes reutilizables, hooks, utils y configuración de UI

---

### Requirement: El proyecto DEBE usar ESLint y Prettier
El proyecto DEBE contar con configuración de linting y formateo de código.

#### Scenario: Configuración de ESLint
- **WHEN** Se ejecuta `npm run lint`
- **THEN** ESLint analiza el código y reporta violaciones de las reglas configuradas

#### Scenario: Configuración de Prettier
- **WHEN** Se formatea el código con Prettier
- **THEN** El código se ajusta al formato definido en `.prettierrc`

#### Scenario: Verificación pre-commit
- **WHEN** El desarrollador intenta hacer commit
- **THEN** El hook de pre-commit verifica que el código pase lint y format

---

### Requirement: El proyecto DEBE incluir archivos de configuración base
El proyecto DEBE incluir los archivos de configuración necesarios para las herramientas utilizadas.

#### Scenario: Archivo tsconfig.json
- **WHEN** Se examina la raíz del proyecto
- **THEN** Existe un archivo `tsconfig.json` con la configuración de TypeScript

#### Scenario: Archivo vite.config.ts
- **WHEN** Se examina la raíz del proyecto
- **THEN** Existe un archivo `vite.config.ts` con la configuración de Vite

#### Scenario: Configuración de Tailwind
- **WHEN** Se examina la configuración de Tailwind
- **THEN** Existe la configuración necesaria para Tailwind CSS v4

#### Scenario: Archivo postcss.config.js
- **WHEN** Se examina la raíz del proyecto
- **THEN** Existe un archivo `postcss.config.js` con la configuración de PostCSS

---

### Requirement: El proyecto DEBE usar variables de entorno
El proyecto DEBE soportar configuración mediante variables de entorno.

#### Scenario: Archivo .env.example
- **WHEN** Se examina la raíz del proyecto
- **THEN** Existe un archivo `.env.example` con las variables de entorno requeridas

#### Scenario: Acceso a variables de entorno
- **WHEN** El código accede a `import.meta.env.VITE_*`
- **THEN** Los valores de las variables de entorno están disponibles en tiempo de ejecución