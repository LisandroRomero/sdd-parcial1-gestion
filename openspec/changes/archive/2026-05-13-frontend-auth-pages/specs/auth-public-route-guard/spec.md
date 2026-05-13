## ADDED Requirements

### Requirement: Las rutas públicas de auth redirigen a / si el usuario ya está autenticado

El sistema SHALL proveer un componente `PublicOnlyRoute` que redirija al usuario autenticado a `/` cuando intente acceder a `/login` o `/register`, evitando que usuarios ya logueados vean los formularios de autenticación.

#### Scenario: Usuario autenticado intenta acceder a /login

- **WHEN** un usuario con `isAuthenticated === true` navega a `/login`
- **THEN** el sistema redirige automáticamente a `/` sin mostrar el formulario de login

#### Scenario: Usuario autenticado intenta acceder a /register

- **WHEN** un usuario con `isAuthenticated === true` navega a `/register`
- **THEN** el sistema redirige automáticamente a `/` sin mostrar el formulario de registro

#### Scenario: Usuario no autenticado puede acceder a /login

- **WHEN** un usuario con `isAuthenticated === false` navega a `/login`
- **THEN** el sistema renderiza la `LoginPage` normalmente

#### Scenario: Usuario no autenticado puede acceder a /register

- **WHEN** un usuario con `isAuthenticated === false` navega a `/register`
- **THEN** el sistema renderiza la `RegisterPage` normalmente

### Requirement: La sesión persiste entre recargas del navegador

El sistema SHALL restaurar la sesión del usuario desde `localStorage` al iniciar la aplicación, evitando que el usuario deba autenticarse de nuevo si ya tenía una sesión activa.

#### Scenario: Recarga con sesión activa no redirige al login

- **WHEN** el usuario recarga la página y `localStorage` contiene `user` y `token` válidos (hidratados por Zustand persist)
- **THEN** el sistema restaura `isAuthenticated === true` y el usuario puede navegar a rutas protegidas sin pasar por login

#### Scenario: Recarga sin sesión redirige al login

- **WHEN** el usuario recarga la página y `localStorage` no contiene datos de sesión (o fueron eliminados)
- **THEN** el sistema no considera al usuario autenticado y redirige a `/login` si intenta acceder a rutas protegidas
