## ADDED Requirements

### Requirement: El header muestra un botón de Logout para usuarios autenticados

El sistema SHALL mostrar en el header de la aplicación un botón "Cerrar sesión" únicamente cuando el usuario está autenticado. Al hacer click, SHALL llamar a `POST /api/v1/auth/logout`, limpiar el `useAuthStore` y redirigir a `/login`.

#### Scenario: Botón de logout visible solo para usuarios autenticados

- **WHEN** el usuario está autenticado (`isAuthenticated === true`)
- **THEN** el header muestra el botón "Cerrar sesión" (o icono equivalente)

#### Scenario: Botón de logout oculto para usuarios no autenticados

- **WHEN** el usuario no está autenticado (`isAuthenticated === false`)
- **THEN** el header NO muestra el botón de logout

#### Scenario: Logout exitoso limpia la sesión y redirige a /login

- **WHEN** el usuario hace click en "Cerrar sesión"
- **THEN** el sistema llama a `POST /api/v1/auth/logout` con el token actual, llama a `useAuthStore.logout()` y redirige a `/login`

#### Scenario: Logout procede aunque el endpoint falle

- **WHEN** el usuario hace click en "Cerrar sesión" y el request a `POST /api/v1/auth/logout` falla (red, 401, 500)
- **THEN** el sistema igualmente llama a `useAuthStore.logout()` y redirige a `/login` — el fallo del endpoint no bloquea el logout local

### Requirement: El header muestra el nombre del usuario autenticado

El sistema SHALL mostrar el nombre del usuario autenticado en el header junto al botón de logout.

#### Scenario: Nombre del usuario visible cuando está autenticado

- **WHEN** el usuario está autenticado y `user.nombre` está disponible
- **THEN** el header muestra el nombre del usuario (ej. "Hola, Juan")
