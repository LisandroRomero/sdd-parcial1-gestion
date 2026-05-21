# frontend-public-home

## Requirements

### Requirement: La ruta / es publica y renderiza el Home

El sistema SHALL exponer la ruta `/` como publica (sin requerir autenticacion). La ruta `/` SHALL renderizar `HomePage`.

#### Scenario: Usuario no autenticado accede a la Home

- **WHEN** un usuario no autenticado navega a `/`
- **THEN** el sistema renderiza `HomePage` y NO redirige a `/login`

#### Scenario: Usuario autenticado accede a la Home

- **WHEN** un usuario autenticado navega a `/`
- **THEN** el sistema renderiza `HomePage`

### Requirement: Home provee CTA hacia /catalogo

El sistema SHALL proveer en `HomePage` al menos un CTA visible que navegue a `/catalogo`.

#### Scenario: CTA visible hacia el catalogo

- **WHEN** un usuario visualiza `HomePage`
- **THEN** existe un CTA que navega a `/catalogo`

### Requirement: Header muestra CTA "Iniciar sesión" cuando usuario no autenticado

El sistema SHALL mostrar en el header de `HomePage` un CTA visible "Iniciar sesión" cuando el usuario NO este autenticado. El CTA SHALL navegar a `/login`.

#### Scenario: Usuario no autenticado visualiza Home y ve CTA de login

- **WHEN** un usuario no autenticado visualiza `HomePage`
- **THEN** el header muestra un CTA "Iniciar sesión" que navega a `/login`

### Requirement: Intentar acceder a rutas privadas desde estado no autenticado redirige a /login

El sistema SHALL tratar como rutas privadas (requieren autenticacion) a `/perfil`, `/pedidos`, `/checkout` y cualquier ruta bajo `/admin/*`. Si un usuario no autenticado intenta navegar a esas rutas, el sistema SHALL redirigir a `/login` sin renderizar el contenido privado.

#### Scenario: Usuario no autenticado intenta acceder a /perfil

- **WHEN** un usuario no autenticado navega a `/perfil`
- **THEN** el sistema redirige a `/login` sin renderizar el contenido de perfil

#### Scenario: Usuario no autenticado intenta acceder a /pedidos

- **WHEN** un usuario no autenticado navega a `/pedidos`
- **THEN** el sistema redirige a `/login` sin renderizar el contenido de pedidos

#### Scenario: Usuario no autenticado intenta acceder a /checkout

- **WHEN** un usuario no autenticado navega a `/checkout`
- **THEN** el sistema redirige a `/login` sin renderizar el contenido de checkout

#### Scenario: Usuario no autenticado intenta acceder a /admin

- **WHEN** un usuario no autenticado navega a `/admin/usuarios`
- **THEN** el sistema redirige a `/login` sin renderizar el contenido de administracion
