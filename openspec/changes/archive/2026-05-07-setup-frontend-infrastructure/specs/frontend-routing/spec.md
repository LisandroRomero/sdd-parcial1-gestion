## ADDED Requirements

### Requirement: La aplicación DEBE usar React Router v6
La aplicación DEBE utilizar React Router versión 6 como solución de routing.

#### Scenario: Instalación de React Router
- **WHEN** Se instalan las dependencias del proyecto
- **THEN** La versión de `react-router-dom` en `package.json` es 6.x

#### Scenario: Configuración del Router
- **WHEN** Se examina la configuración de routing
- **THEN** Se utiliza `BrowserRouter` para envolver la aplicación

#### Scenario: Navegación entre páginas
- **WHEN** El usuario hace clic en un enlace con `<Link>` o `<NavLink>`
- **THEN** La URL cambia sin recargar la página y el componente对应的 se renderiza

---

### Requirement: DEBE haber rutas base para las secciones principales
La aplicación DEBE definir rutas para las secciones principales del proyecto.

#### Scenario: Ruta de autenticación
- **WHEN** El usuario navega a `/auth`
- **THEN** Se renderiza el componente de autenticación (login, registro)

#### Scenario: Ruta del catálogo de productos
- **WHEN** El usuario navega a `/products`
- **THEN** Se renderiza el catálogo de productos

#### Scenario: Ruta del carrito de compras
- **WHEN** El usuario navega a `/cart`
- **THEN** Se renderiza el componente del carrito

#### Scenario: Ruta de pedidos
- **WHEN** El usuario navega a `/orders`
- **THEN** Se renderiza el componente de pedidos del usuario

#### Scenario: Ruta de perfil de usuario
- **WHEN** El usuario navega a `/profile`
- **THEN** Se renderiza el componente de perfil del usuario

#### Scenario: Ruta del panel de administración
- **WHEN** El usuario navega a `/admin`
- **THEN** Se renderiza el panel de administración

#### Scenario: Ruta raíz
- **WHEN** El usuario navega a `/`
- **THEN** Se renderiza la página de inicio o landing

---

### Requirement: Las rutas DEBEN usar lazy loading para code splitting
Las rutas DEBEN implementar carga diferida para optimizar el tamaño del bundle inicial.

#### Scenario: Importación lazy de componentes de página
- **WHEN** Se define una ruta
- **THEN** El componente de página se importa usando `React.lazy()` y `<Suspense>`

#### Scenario: Suspense fallback
- **WHEN** Se carga un componente lazy
- **THEN** Se muestra un componente de carga mientras el chunk se descarga

#### Scenario: Code splitting efectivo
- **WHEN** Se analiza el build de producción
- **THEN** Existen múltiples chunks separados para diferentes rutas

---

### Requirement: DEBE existir un componente Layout base con Outlet
La aplicación DEBE tener un componente Layout base que contenga la estructura común de la aplicación.

#### Scenario: Estructura del Layout
- **WHEN** Se examina el componente Layout
- **THEN** Contiene un `<Outlet />` de React Router para renderizar las rutas Hijas

#### Scenario: Navegación persistente
- **WHEN** El usuario navega entre páginas
- **THEN** El Layout permanece intacto y solo cambia el contenido del Outlet

#### Scenario: Header y Footer en Layout
- **WHEN** Se renderiza el Layout
- **THEN** El Header y Footer se muestran en todas las páginas

#### Scenario: Rutas anidadas
- **WHEN** Se define una ruta dentro de otra ruta con Layout
- **THEN** La ruta hija se renderiza dentro del Outlet del Layout

---

### Requirement: DEBE haber manejo de rutas no encontradas
La aplicación DEBE mostrar una página 404 cuando la ruta no existe.

#### Scenario: Ruta inexistente
- **WHEN** El usuario navega a una URL que no existe
- **THEN** Se renderiza un componente de página no encontrada con mensaje apropiado

#### Scenario: Navigation a página 404
- **WHEN** Se utiliza `useNavigate` para ir a una ruta inválida
- **THEN** Se muestra la página de error 404

---

### Requirement: DEBE haber configuración de rutas privada
La aplicación DEBE permitir proteger rutas para usuarios autenticados.

#### Scenario: Ruta protegida sin autenticación
- **WHEN** Un usuario no autenticado intenta acceder a una ruta protegida
- **THEN** Es redirigido a la página de login

#### Scenario: Ruta protegida con autenticación
- **WHEN** Un usuario autenticado accede a una ruta protegida
- **THEN** Puede acceder al contenido de la ruta